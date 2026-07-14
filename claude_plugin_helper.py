import requests
import json
import time

SERVER_URL = "https://unawake-impart-trio.ngrok-free.dev"
SECRET = "changeme123"
PLUGIN_SESSION = None

def set_session(session_id):
    global PLUGIN_SESSION
    PLUGIN_SESSION = session_id

def send_command(command, args=None):
    if not PLUGIN_SESSION:
        print("❌ No plugin session. Check Studio console for session ID and call: set_session('YOUR_SESSION_ID')")
        return None

    try:
        response = requests.post(
            f"{SERVER_URL}/plugin/command",
            json={
                "session": PLUGIN_SESSION,
                "command": command,
                "args": args or {}
            },
            headers={"x-secret": SECRET},
            timeout=5
        )
        data = response.json()
        cmd_id = data.get("command_id")

        if cmd_id:
            time.sleep(0.5)
            result_response = requests.get(
                f"{SERVER_URL}/plugin/get_result",
                params={"session": PLUGIN_SESSION, "cmd_id": cmd_id},
                headers={"x-secret": SECRET},
                timeout=5
            )
            result_data = result_response.json()
            return result_data.get("result")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def list_scripts():
    return send_command("list_scripts")

def read_script(path):
    return send_command("read_script", {"path": path})

def modify_script(path, source):
    return send_command("modify_script", {"path": path, "source": source})

def find_instances(name):
    return send_command("find_instances", {"name": name})

if __name__ == "__main__":
    print("Claude Plugin Helper")
    print("Set session first: set_session('SESSION_ID_FROM_STUDIO')")
    print("\nAvailable commands:")
    print("  list_scripts() - list all scripts in game")
    print("  read_script(path) - read script source")
    print("  modify_script(path, source) - modify script")
    print("  find_instances(name) - find instances by name")
