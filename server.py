from flask import Flask, request, jsonify
import json
import os
import uuid
import threading

app = Flask(__name__)
QUEUE_FILE = "queue.json"
DATA_FILE = "namestore_data.json"
LUA_FILE = "NameStore.lua"
SPAWNERS_FILE = "spawners_data.json"
SECRET = os.getenv("SERVER_SECRET", "changeme123")

plugin_commands = {}
plugin_results = {}
plugin_lock = threading.Lock()


def load_queue():
    if not os.path.exists(QUEUE_FILE):
        return []
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_queue(q):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(q, f)


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def lua_str(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def regenerate_lua(data):
    lines = []
    lines.append('-- 7allurez and 𝓨𝓾𝓹𝓸™ made this')
    lines.append('local Settings = {')
    lines.append('')

    # CustomNames
    lines.append('\tCustomNames = {')
    for uid, name in data["CustomNames"].items():
        lines.append(f'\t\t["{uid}"] = "{lua_str(name)}";')
    lines.append('\t};')
    lines.append('')

    # GroupTags
    lines.append('\tGroupTags = {')
    for gid, v in data.get("GroupTags", {}).items():
        lines.append(f'\t\t["{gid}"] = {{Tag = "{lua_str(v["tag"])}", Color = Color3.fromRGB({v["r"]}, {v["g"]}, {v["b"]})}};')
    lines.append('\t};')
    lines.append('')

    # UserTags
    lines.append('\tUserTags = {')
    for uid, v in data["UserTags"].items():
        lines.append(f'\t\t["{uid}"] = {{Tag = "{lua_str(v["tag"])}", Color = Color3.fromRGB({v["r"]}, {v["g"]}, {v["b"]})}};')
    lines.append('\t};')
    lines.append('')

    # RankTagColors
    lines.append('\tRankTagColors = {')
    for uid, v in data["RankTagColors"].items():
        lines.append(f'\t\t["{uid}"] = Color3.fromRGB({v["r"]}, {v["g"]}, {v["b"]});')
    lines.append('\t};')
    lines.append('')

    # CustomRankUsername
    lines.append('\tCustomRankUsername = {')
    for uid, name in data["CustomRankUsername"].items():
        lines.append(f'\t\t["{uid}"] = "{lua_str(name)}";')
    lines.append('\t};')
    lines.append('')

    lines.append('}')
    lines.append('')
    lines.append('return Settings')

    with open(LUA_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[Server] NameStore.lua regenerated")


def apply_to_data(entry):
    data = load_data()
    t = entry["type"]
    uid = str(entry["userid"])

    if t == "CustomName":
        data["CustomNames"][uid] = entry["value"]
    elif t == "UserTag":
        data["UserTags"][uid] = {"tag": entry["tag"], "r": entry["r"], "g": entry["g"], "b": entry["b"]}
    elif t == "RankTagColor":
        data["RankTagColors"][uid] = {"r": entry["r"], "g": entry["g"], "b": entry["b"]}
    elif t == "CustomUsername":
        data["CustomRankUsername"][uid] = entry["value"]
    elif t == "GroupTag":
        data.setdefault("GroupTags", {})[uid] = {"tag": entry["tag"], "r": entry["r"], "g": entry["g"], "b": entry["b"]}
    elif t == "RemoveGroup":
        data.get("GroupTags", {}).pop(uid, None)
    elif t == "Remove":
        data["CustomNames"].pop(uid, None)
        data["UserTags"].pop(uid, None)
        data["RankTagColors"].pop(uid, None)
        data["CustomRankUsername"].pop(uid, None)

    save_data(data)
    regenerate_lua(data)


# ---------------- SPAWNERS ----------------
# spawners_data.json shape:
# { "ToolName": { "whitelist": {"<userid>": true, ...}, "gamePassId": <int or absent> } }

def load_spawners():
    if not os.path.exists(SPAWNERS_FILE):
        return {}
    with open(SPAWNERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_spawners(data):
    with open(SPAWNERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def apply_spawner(entry):
    data = load_spawners()
    tool = entry["tool"]
    action = entry["action"]
    cfg = data.setdefault(tool, {"whitelist": {}})
    cfg.setdefault("whitelist", {})

    if action == "whitelist_add":
        cfg["whitelist"][str(entry["userid"])] = True
    elif action == "whitelist_remove":
        cfg["whitelist"].pop(str(entry["userid"]), None)
    elif action == "set_gamepass":
        cfg["gamePassId"] = int(entry["gamepass"])
    elif action == "remove_gamepass":
        cfg.pop("gamePassId", None)
    elif action == "clear":
        data.pop(tool, None)

    save_spawners(data)


@app.route("/getspawners", methods=["GET"])
def getspawners():
    if request.args.get("secret") != SECRET:
        return jsonify({"error": "unauthorized"}), 401
    return jsonify(load_spawners())


@app.route("/pushspawner", methods=["POST"])
def pushspawner():
    if request.headers.get("x-secret") != SECRET:
        return jsonify({"error": "unauthorized"}), 401
    apply_spawner(request.json)
    return jsonify({"ok": True})


@app.route("/push", methods=["POST"])
def push():
    if request.headers.get("x-secret") != SECRET:
        return jsonify({"error": "unauthorized"}), 401
    entry = request.json
    # Save to queue for Roblox to poll
    q = load_queue()
    q.append(entry)
    save_queue(q)
    # Also persist to file
    apply_to_data(entry)
    return jsonify({"ok": True})


@app.route("/getdata", methods=["GET"])
def getdata():
    if request.args.get("secret") != SECRET:
        return jsonify({"error": "unauthorized"}), 401
    return jsonify(load_data())


@app.route("/getsource", methods=["GET"])
def getsource():
    if request.args.get("secret") != SECRET:
        return jsonify({"error": "unauthorized"}), 401
    if not os.path.exists(LUA_FILE):
        return jsonify({"source": None})
    with open(LUA_FILE, "r", encoding="utf-8") as f:
        return jsonify({"source": f.read()})


@app.route("/poll", methods=["GET"])
def poll():
    if request.args.get("secret") != SECRET:
        return jsonify({"error": "unauthorized"}), 401
    q = load_queue()
    save_queue([])
    return jsonify(q)


@app.route("/plugin/poll", methods=["GET"])
def plugin_poll():
    session = request.args.get("session")
    if not session:
        return jsonify({"error": "no session"}), 400

    with plugin_lock:
        if session in plugin_commands:
            cmd = plugin_commands.pop(session)
            return jsonify(cmd)
    return jsonify({})


@app.route("/plugin/result", methods=["POST"])
def plugin_result():
    if request.headers.get("x-secret") != SECRET:
        return jsonify({"error": "unauthorized"}), 401

    data = request.json
    session = data.get("session")
    cmd_id = data.get("command_id")
    result = data.get("result")

    if session and cmd_id:
        with plugin_lock:
            plugin_results[f"{session}:{cmd_id}"] = result

    return jsonify({"ok": True})


@app.route("/plugin/command", methods=["POST"])
def plugin_command():
    if request.headers.get("x-secret") != SECRET:
        return jsonify({"error": "unauthorized"}), 401

    data = request.json
    session = data.get("session")
    command = data.get("command")
    args = data.get("args", {})

    if not session or not command:
        return jsonify({"error": "missing session or command"}), 400

    cmd_id = str(uuid.uuid4())

    with plugin_lock:
        plugin_commands[session] = {
            "id": cmd_id,
            "command": command,
            "args": args
        }

    return jsonify({"command_id": cmd_id})


@app.route("/plugin/get_result", methods=["GET"])
def plugin_get_result():
    if request.headers.get("x-secret") != SECRET:
        return jsonify({"error": "unauthorized"}), 401

    session = request.args.get("session")
    cmd_id = request.args.get("cmd_id")

    if not session or not cmd_id:
        return jsonify({"error": "missing session or cmd_id"}), 400

    key = f"{session}:{cmd_id}"
    with plugin_lock:
        if key in plugin_results:
            result = plugin_results.pop(key)
            return jsonify({"result": result})

    return jsonify({"result": None})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
