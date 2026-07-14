# Roblox Studio Scripts Setup Guide

All scripts below need to be placed in your Roblox game. Follow the location instructions for each one.

## Script Locations

### 1. **NameStore.lua** 
   - **Location:** ServerStorage → NameStore (ModuleScript)
   - **Purpose:** Stores all custom names, tags, colors, and rank usernames
   - **Action:** Copy content from `Scripts/[1] NameStore.lua`

### 2. **TagDisplayScript.lua**
   - **Location:** ServerScriptService (Script)
   - **Purpose:** Polls Flask server every 5 seconds and displays custom tags/names above players
   - **Action:** Copy content from `Scripts/[2] TagDisplayScript.lua`

### 3. **NameStoreUpdater.lua**
   - **Location:** ServerScriptService (Script)
   - **Purpose:** Polls `/poll` endpoint every 10 seconds to sync NameStore updates
   - **Action:** Copy content from `Scripts/[3] NameStoreUpdater.lua`

### 4. **NameStoreSyncScript.lua**
   - **Location:** ServerScriptService (Script)
   - **Purpose:** Monitors NameStore ModuleScript changes every 3 seconds, syncs to Flask
   - **Action:** Copy content from `Scripts/[4] NameStoreSyncScript.lua`

---

## Setup Steps

1. Open your Roblox game in Studio
2. For each script above, create a new script in the specified location
3. Copy the **entire content** from the corresponding file in the `Scripts/` folder (numbered files like [1], [2], etc.)
4. Paste into the Studio script and **do not modify**
5. Save and test

---

## Server URL Configuration

All scripts use: `https://unawake-impart-trio.ngrok-free.dev`

If your ngrok URL changes, update the `SERVER_URL` variable in each script.

---

## Testing

- Run the game and check the **Output window** for any errors
- Watch player names/tags appear above heads as you add them via Discord bot
- Use `/setcustom`, `/settag`, `/setusername` in Discord to test
