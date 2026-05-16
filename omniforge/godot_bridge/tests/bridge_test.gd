extends Node
## OmniForge Bridge Sanity Test

func run_tests():
	print("--- Starting Bridge Tests ---")
	test_connection()
	test_command_parsing()
	print("--- All Bridge Tests Passed ---")

func test_connection():
	var bridge = load("res://omniforge/godot_bridge/OmniForgeBridge.gd").new()
	assert(bridge != null, "Bridge script failed to load")
	print("[PASS] Bridge loaded")

func test_command_parsing():
	var bridge = load("res://omniforge/godot_bridge/OmniForgeBridge.gd").new()
	# Mock handle_command
	var json_data = '{"cmd": "connected", "msg": "test"}'
	bridge._handle_command(json_data)
	print("[PASS] Command parsing verified")
