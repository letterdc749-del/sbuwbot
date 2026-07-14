local plugin = plugin
local SERVER_URL = "https://unawake-impart-trio.ngrok-free.dev"
local POLL_INTERVAL = 2
local SESSION_ID = tostring(math.random(100000, 999999))

local isRunning = true
local toolbar, statusButton

if plugin then
	toolbar = plugin:CreateToolbar("Claude Control")
	statusButton = toolbar:CreateButton("Claude Status", "Claude Plugin Connected", "")
	statusButton.Click:Connect(function()
		isRunning = not isRunning
		statusButton:SetActive(isRunning)
	end)
	statusButton:SetActive(true)
end

local function readScript(scriptPath)
	local parts = string.split(scriptPath, ".")
	local current = game

	for _, part in ipairs(parts) do
		if current[part] then
			current = current[part]
		else
			return nil
		end
	end

	if current:IsA("Script") or current:IsA("LocalScript") or current:IsA("ModuleScript") then
		return current.Source
	end
	return nil
end

local function modifyScript(scriptPath, newSource)
	local parts = string.split(scriptPath, ".")
	local current = game

	for _, part in ipairs(parts) do
		if current[part] then
			current = current[part]
		else
			return false
		end
	end

	if current:IsA("Script") or current:IsA("LocalScript") or current:IsA("ModuleScript") then
		current.Source = newSource
		return true
	end
	return false
end

local function getInstance(path)
	local parts = string.split(path, ".")
	local current = game
	for _, part in ipairs(parts) do
		if current[part] then
			current = current[part]
		else
			return nil
		end
	end
	return current
end

local function getProperties(instance)
	local props = {}
	local success, allProps = pcall(function()
		return instance:GetChildren()
	end)

	for _, prop in ipairs({"Name", "Parent", "ClassName"}) do
		pcall(function()
			props[prop] = tostring(instance[prop])
		end)
	end

	return props
end

local function listScripts(instance, prefix)
	local scripts = {}

	if instance:IsA("Script") or instance:IsA("LocalScript") or instance:IsA("ModuleScript") then
		table.insert(scripts, {
			path = prefix .. instance.Name,
			name = instance.Name,
			type = instance.ClassName
		})
	end

	for _, child in ipairs(instance:GetChildren()) do
		local childScripts = listScripts(child, prefix .. instance.Name .. ".")
		for _, script in ipairs(childScripts) do
			table.insert(scripts, script)
		end
	end

	return scripts
end

local function executeCommand(command, args)
	if command == "list_scripts" then
		return listScripts(game, "game.")

	elseif command == "read_script" then
		local source = readScript(args.path)
		return source and {content = source} or {error = "Script not found"}

	elseif command == "modify_script" then
		local success = modifyScript(args.path, args.source)
		return {success = success}

	elseif command == "find_instances" then
		local results = {}
		local function search(inst, target)
			if inst.Name == target then
				table.insert(results, inst:GetFullName())
			end
			for _, child in ipairs(inst:GetChildren()) do
				search(child, target)
			end
		end
		search(game, args.name)
		return {found = results}

	elseif command == "get_children" then
		local parts = string.split(args.path, ".")
		local current = game
		for _, part in ipairs(parts) do
			if current[part] then
				current = current[part]
			else
				return {error = "Path not found"}
			end
		end
		local children = {}
		for i, child in ipairs(current:GetChildren()) do
			if args.limit and i > args.limit then break end
			table.insert(children, {
				name = child.Name,
				class = child.ClassName,
				path = current:GetFullName() .. "." .. child.Name
			})
		end
		return {children = children}

	elseif command == "get_instance" then
		local inst = getInstance(args.path)
		if not inst then
			return {error = "Instance not found"}
		end
		local children = {}
		for i, child in ipairs(inst:GetChildren()) do
			if (args.limit or 10) and i > (args.limit or 10) then break end
			table.insert(children, {name = child.Name, class = child.ClassName})
		end
		return {
			name = inst.Name,
			class = inst.ClassName,
			path = inst:GetFullName(),
			children = children
		}

	elseif command == "set_property" then
		local inst = getInstance(args.path)
		if not inst then
			return {error = "Instance not found"}
		end
		local success, err = pcall(function()
			inst[args.property] = args.value
		end)
		return {success = success, error = err}

	elseif command == "get_property" then
		local inst = getInstance(args.path)
		if not inst then
			return {error = "Instance not found"}
		end
		local success, value = pcall(function()
			return inst[args.property]
		end)
		return {success = success, value = tostring(value), error = not success and tostring(value) or nil}

	elseif command == "tree" then
		local function buildTree(inst, depth, maxDepth)
			if depth > (maxDepth or 5) then return nil end
			local children = {}
			for _, child in ipairs(inst:GetChildren()) do
				table.insert(children, {
					name = child.Name,
					class = child.ClassName,
					children = buildTree(child, depth + 1, maxDepth)
				})
			end
			return children
		end
		local inst = getInstance(args.path or "game")
		if not inst then
			return {error = "Instance not found"}
		end
		return {tree = buildTree(inst, 0, args.depth or 3)}

	else
		return {error = "Unknown command: " .. tostring(command)}
	end
end

local http = game:GetService("HttpService")

local function pollServer()
	print("🔄 Plugin polling started — Session: " .. SESSION_ID)
	while isRunning do
		local success, response = pcall(function()
			return http:GetAsync(SERVER_URL .. "/plugin/poll?session=" .. SESSION_ID, false)
		end)

		if success and response then
			local decodeSuccess, decoded = pcall(function()
				return http:JSONDecode(response)
			end)

			if decodeSuccess and decoded and decoded.command then
				print("📨 Got command: " .. decoded.command)
				local result = executeCommand(decoded.command, decoded.args or {})

				local postSuccess, postErr = pcall(function()
					http:PostAsync(
						SERVER_URL .. "/plugin/result",
						http:JSONEncode({
							session = SESSION_ID,
							command_id = decoded.id,
							result = result
						}),
						Enum.HttpContentType.ApplicationJson,
						false,
						{["x-secret"] = "changeme123"}
					)
				end)

				if not postSuccess then
					print("❌ Failed to post result: " .. tostring(postErr))
				end
			end
		end

		wait(POLL_INTERVAL)
	end
end

spawn(pollServer)

print("✅ Claude Studio Plugin loaded — Session: " .. SESSION_ID)
