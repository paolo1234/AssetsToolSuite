extends Node
## OmniForge Live Bridge — AutoLoad
## Handles real-time asset previewing from the OmniForge desktop app.

@export var enabled: bool = true
@export var server_url: str = "ws://localhost:47832"

var _ws: WebSocketPeer = WebSocketPeer.new()
var _is_connected: bool = false
var _original_scene_path: String
var _sandbox_scene: PackedScene

func _ready() -> void:
	if not enabled:
		return
	
	process_mode = PROCESS_MODE_ALWAYS
	_connect_to_host()

func _process(_delta: float) -> void:
	if not enabled:
		return
	
	_ws.poll()
	var state = _ws.get_ready_state()
	
	if state == WebSocketPeer.STATE_OPEN:
		if not _is_connected:
			_is_connected = true
			print("[OmniForge] Bridge Connected")
		
		while _ws.get_available_packet_count() > 0:
			var packet = _ws.get_packet()
			var json_str = packet.get_string_from_utf8()
			_handle_command(json_str)
			
	elif state == WebSocketPeer.STATE_CLOSED:
		if _is_connected:
			_is_connected = false
			print("[OmniForge] Bridge Disconnected. Retrying...")
			_reconnect()

func _connect_to_host() -> void:
	var err = _ws.connect_to_url(server_url)
	if err != OK:
		printerr("[OmniForge] Could not connect to bridge: ", err)

func _reconnect() -> void:
	await get_tree().create_timer(5.0).timeout
	_connect_to_host()

func _handle_command(json_str: String) -> void:
	var json = JSON.parse_string(json_str)
	if not json or not json.has("cmd"):
		return
		
	var cmd = json.cmd
	print("[OmniForge] Received: ", cmd)
	
	match cmd:
		"preview_sprite":
			_preview_sprite(json)
		"preview_audio":
			_preview_audio(json)
		"close_preview":
			_close_preview()
		"reload_asset":
			_reload_asset(json.path)

func _preview_sprite(data: Dictionary) -> void:
	# 1. Store current scene if not already in sandbox
	if get_tree().current_scene.name != "OmniForge_Sandbox":
		_original_scene_path = get_tree().current_scene.scene_file_path
		
	# 2. Switch to sandbox
	if not _sandbox_scene:
		_sandbox_scene = load("res://omniforge/OmniForge_Sandbox.tscn")
	
	if get_tree().current_scene.name != "OmniForge_Sandbox":
		get_tree().change_scene_to_packed(_sandbox_scene)
		await get_tree().process_frame # Wait for scene switch
	
	# 3. Update sandbox with sprite data
	var sandbox = get_tree().current_scene
	if sandbox.has_method("setup_sprite"):
		sandbox.setup_sprite(data.path)

func _preview_audio(data: Dictionary) -> void:
	var sandbox = get_tree().current_scene
	if sandbox.name == "OmniForge_Sandbox" and sandbox.has_method("play_audio"):
		sandbox.play_audio(data.path)

func _close_preview() -> void:
	if _original_scene_path != "":
		get_tree().change_scene_to_file(_original_scene_path)
		_original_scene_path = ""

func _reload_asset(path: String) -> void:
	var res = load(path)
	if res:
		res.take_over_path(path) # Force reload logic in Godot
		print("[OmniForge] Reloaded: ", path)
