-- Place this Script in ServerScriptService
-- Polls your local Flask server and applies updates to NameStore live

local HttpService = game:GetService("HttpService")
local NameStore = require(game.ServerStorage.NameStore)

local SERVER_URL = "http://192.168.0.79:5000/poll?secret=changeme123"
local POLL_INTERVAL = 10

local function parseRGB(r, g, b)
	return Color3.fromRGB(tonumber(r), tonumber(g), tonumber(b))
end

local function applyUpdate(entry)
	local t = entry.type
	local userid = tostring(entry.userid)

	if t == "CustomName" then
		NameStore.CustomNames[userid] = entry.value
		print("[NameStore] CustomName set for", userid, "→", entry.value)

	elseif t == "UserTag" then
		NameStore.UserTags[userid] = {
			Tag = entry.tag,
			Color = parseRGB(entry.r, entry.g, entry.b)
		}
		print("[NameStore] UserTag set for", userid, "→", entry.tag)

	elseif t == "RankTagColor" then
		NameStore.RankTagColors[userid] = parseRGB(entry.r, entry.g, entry.b)
		print("[NameStore] RankTagColor set for", userid)

	elseif t == "CustomUsername" then
		NameStore.CustomRankUsername[userid] = entry.value
		print("[NameStore] CustomUsername set for", userid, "→", entry.value)

	elseif t == "Remove" then
		NameStore.CustomNames[userid] = nil
		NameStore.UserTags[userid] = nil
		NameStore.RankTagColors[userid] = nil
		NameStore.CustomRankUsername[userid] = nil
		print("[NameStore] Removed all customs for", userid)
	end
end

while true do
	local ok, result = pcall(function()
		local response = HttpService:GetAsync(SERVER_URL)
		local data = HttpService:JSONDecode(response)
		for _, entry in ipairs(data) do
			applyUpdate(entry)
		end
	end)

	if not ok then
		warn("[NameStoreUpdater] Error:", result)
	end

	task.wait(POLL_INTERVAL)
end
