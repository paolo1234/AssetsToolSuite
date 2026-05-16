"""
OmniForge Backend — Godot Bridge Server
Dedicated WebSocket server for communication with Godot Engine.
Port: 47832
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Set

import websockets
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger("omniforge.bridge")

class GodotBridgeServer:
    """
    Handles live communication with the Godot AutoLoad bridge.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 47832) -> None:
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.command_queue: asyncio.Queue = asyncio.Queue()

    async def register(self, ws: WebSocketServerProtocol) -> None:
        self.clients.add(ws)
        logger.info(f"Godot instance connected: {ws.remote_address}")
        # Send a welcome/ping
        await ws.send(json.dumps({"cmd": "connected", "msg": "OmniForge Bridge Active"}))

    async def unregister(self, ws: WebSocketServerProtocol) -> None:
        self.clients.remove(ws)
        logger.info(f"Godot instance disconnected: {ws.remote_address}")

    async def handler(self, ws: WebSocketServerProtocol) -> None:
        await self.register(ws)
        try:
            async for message in ws:
                data = json.loads(message)
                logger.debug(f"Received from Godot: {data}")
                # Handle potential Godot-to-OmniForge messages (e.g. status updates)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(ws)

    async def broadcast(self, command: dict) -> None:
        """Send a command to all connected Godot instances."""
        if not self.clients:
            logger.warning("No Godot instances connected. Command queued.")
            return

        message = json.dumps(command)
        await asyncio.gather(
            *[client.send(message) for client in self.clients],
            return_exceptions=True
        )

    async def start(self) -> None:
        logger.info(f"Starting Godot Bridge on ws://{self.host}:{self.port}")
        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future()  # run forever

# Singleton instance
bridge_server = GodotBridgeServer()
