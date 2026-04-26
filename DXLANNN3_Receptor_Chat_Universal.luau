
--[[
    ╔══════════════════════════════════════════════════════════════════════╗
    ║             📡  DXLANNN3 - RECEPTOR DE CHAT UNIVERSAL              ║
    ╚══════════════════════════════════════════════════════════════════════╝
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TextChatService = game:GetService("TextChatService")
local RemoteEvent = ReplicatedStorage:WaitForChild("AnuncioChatEvent", 15)

if RemoteEvent then
    RemoteEvent.OnClientEvent:Connect(function(mensaje)
        local channels = TextChatService:FindFirstChild("TextChannels")
        local generalChannel = channels and channels:FindFirstChild("RBXGeneral")

        if generalChannel then
            generalChannel:DisplaySystemMessage(mensaje)
        end
    end)
end
