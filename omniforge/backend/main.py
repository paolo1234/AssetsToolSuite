"""
OmniForge Backend — Main Application
FastAPI app with REST + WebSocket, CORS, and Godot Bridge server.
"""

from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .routers import project as project_router

# ── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("omniforge")


# ── WebSocket Connection Manager ─────────────────────────────────────────────

class ConnectionManager:
    """Manages WebSocket connections from the frontend."""

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("Frontend WebSocket connected (%d total)", len(self.active_connections))

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info("Frontend WebSocket disconnected (%d remaining)", len(self.active_connections))

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Send a message to all connected frontends."""
        dead: list[WebSocket] = []
        for conn in self.active_connections:
            try:
                await conn.send_json(message)
            except Exception:
                dead.append(conn)
        for d in dead:
            self.disconnect(d)


ws_manager = ConnectionManager()


# ── Godot Bridge WebSocket Server ────────────────────────────────────────────

class GodotBridgeServer:
    """
    Dedicated WebSocket server for Godot Engine communication.
    Runs on a separate port (default 47832).
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 47832) -> None:
        self.host = host
        self.port = port
        self.godot_ws: Any = None  # The single Godot connection
        self._command_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=20)
        self._server: Any = None

    async def start(self) -> None:
        """Start the Godot bridge WebSocket server."""
        try:
            import websockets
            self._server = await websockets.serve(
                self._handle_godot,
                self.host,
                self.port,
            )
            logger.info("Godot Bridge WebSocket running on ws://%s:%d", self.host, self.port)
        except Exception as e:
            logger.warning("Could not start Godot Bridge server: %s", e)

    async def _handle_godot(self, websocket: Any) -> None:
        """Handle a Godot Engine WebSocket connection."""
        self.godot_ws = websocket
        logger.info("Godot Engine connected to bridge")

        try:
            # Send any queued commands
            while not self._command_queue.empty():
                cmd = self._command_queue.get_nowait()
                await websocket.send(json.dumps(cmd))

            # Listen for messages from Godot
            async for message in websocket:
                data = json.loads(message)
                logger.info("Godot → OmniForge: %s", data.get("type", "unknown"))
                # Broadcast to frontend
                await ws_manager.broadcast({"source": "godot", "data": data})

        except Exception as e:
            logger.info("Godot disconnected: %s", e)
        finally:
            self.godot_ws = None

    async def send_to_godot(self, command: dict[str, Any]) -> bool:
        """Send a command to the connected Godot instance."""
        if self.godot_ws is not None:
            try:
                await self.godot_ws.send(json.dumps(command))
                return True
            except Exception:
                pass

        # Queue the command if Godot isn't connected (up to 20)
        try:
            self._command_queue.put_nowait(command)
        except asyncio.QueueFull:
            logger.warning("Godot command queue full — dropping command")
        return False

    async def stop(self) -> None:
        if self._server:
            self._server.close()
            await self._server.wait_closed()


godot_bridge = GodotBridgeServer(
    host=settings.BACKEND_HOST,
    port=settings.BRIDGE_PORT,
)


# ── Application Lifespan ─────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    # Startup
    settings.ensure_dirs()
    logger.info("OmniForge Backend starting on port %d", settings.BACKEND_PORT)
    logger.info("Projects directory: %s", settings.PROJECTS_DIR)

    await godot_bridge.start()

    yield

    # Shutdown
    await godot_bridge.stop()
    logger.info("OmniForge Backend stopped")


# ── FastAPI App ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="OmniForge",
    description="Game Assets Tool Suite — Backend API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(project_router.router)


# ── Health Check ─────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check() -> dict[str, Any]:
    return {
        "status": "ok",
        "version": "0.1.0",
        "godot_connected": godot_bridge.godot_ws is not None,
        "frontend_connections": len(ws_manager.active_connections),
    }


# ── Frontend WebSocket ───────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket for real-time updates to the frontend."""
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "")

            # Route messages from frontend
            if msg_type == "bridge_command":
                # Forward to Godot
                await godot_bridge.send_to_godot(data.get("command", {}))
            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})
            else:
                logger.info("Frontend message: %s", msg_type)

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket error: %s", e)
        ws_manager.disconnect(websocket)


# ── Godot Bridge REST Endpoint ───────────────────────────────────────────────

@app.post("/api/bridge/command")
async def send_bridge_command(command: dict[str, Any]) -> dict[str, Any]:
    """Send a command to Godot via the bridge."""
    sent = await godot_bridge.send_to_godot(command)
    return {"sent": sent, "godot_connected": godot_bridge.godot_ws is not None}


# ── Run directly ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "omniforge.backend.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True,
    )
