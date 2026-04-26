
--[[
    ╔══════════════════════════════════════════════════════════════════════╗
    ║             📢  DXLANNN3 - AUTO ANNOUNCER SYSTEM                   ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║ VERSIÓN: 1.0 (Fixed)                                               ║
    ║ AUTOR: Dxlannn3                                                      ║
    ║ DESCRIPCIÓN: Envía mensajes automáticos al chat cada cierto tiempo.  ║
    ╚══════════════════════════════════════════════════════════════════════╝

    [ INSTRUCCIONES ]
    1. SERVER SCRIPT: Pon este código como un script en 'ServerScriptService'.
    2. REMOTE EVENT: Crea en la seccion 'ReplicatedStorage' un remote event llamado "AnuncioChatEvent".
    3. CLIENT SCRIPT: En la carpeta StarterPlayer -> StarterPlayerScript pon el Script Complementario puedes buscar el codigo en 
    mi GitHub o buscar en la Toolbox de Roblox Studio.
]]

-- [ CONFIGURACIÓN ]
local TIEMPO_ENTRE_ANUNCIOS = 30 -- Segundos (Ej: 180 = 3 minutos)

local MENSAJES = {
    "<font color='#55ff7f'>[INFO]</font> TEXTO AQUI",
    "<font color='#55aaff'>[SOCIAL]</font> ¡TEXTO AQUI! 👥",
    "<font color='#ffaa00'>[TIP]</font> TEXTO AQUI. 💡",
    "<font color='#ff55ff'>[CREDITOS]</font> TEXTO AQUI. ✨"
}

-- [ SERVICIOS ]
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RemoteEvent = ReplicatedStorage:WaitForChild("AnuncioChatEvent", 15)

-- [ LÓGICA ]
print("🚀 Dxlannn3 Anunciador V1.0 - Cargado correctamente")

local indice = 1

while true do
    task.wait(TIEMPO_ENTRE_ANUNCIOS)

    if RemoteEvent then
        -- Elegimos el mensaje actual
        local mensajeSeleccionado = MENSAJES[indice]

        -- Enviamos a todos
        RemoteEvent:FireAllClients(mensajeSeleccionado)

        -- Avanzamos al siguiente mensaje (y reiniciamos si llegamos al final)
        indice = indice + 1
        if indice > #MENSAJES then
            indice = 1
        end
    else
        warn("⚠️ [Dxlannn3]: No se encontró AnuncioChatEvent para enviar anuncios.")
    end
end

-- Script creado por: Dxlannn3 | espero te sirva muchas gracias por usarlo :).
