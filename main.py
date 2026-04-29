import flet as ft
import os
import threading # Para que la búsqueda en vivo no laguee la barra de música
from motor import buscar_cancion, obtener_url_audio

# --- CONFIGURACIÓN DE ARCHIVOS ---
if not os.path.exists("downloads"):
    os.makedirs("downloads")

HISTORIAL_FILE = "historial.txt"
if not os.path.exists(HISTORIAL_FILE):
    with open(HISTORIAL_FILE, "w") as f: f.write("")

def main(page: ft.Page):
    page.title = "Velqi - Bypass Engine"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 450
    page.window_height = 800
    
    # --- LÓGICA DE HISTORIAL Y AUTO-ADIVINAR ---
    def guardar_en_historial(query):
        busquedas = obtener_historial()
        if query not in busquedas:
            with open(HISTORIAL_FILE, "a") as f:
                f.write(f"{query}\n")

    def obtener_historial():
        if not os.path.exists(HISTORIAL_FILE): return []
        with open(HISTORIAL_FILE, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]

    # --- COMPONENTE AUDIO (FIX DE LAG) ---
    def on_position_changed(e):
        try:
            if not slider_progreso.active: 
                # Forzamos que el slider siempre reciba el valor real
                slider_progreso.value = float(e.data)
                page.update()
        except: pass # Evita que el error de "UI thread" congele la barra

    def on_duration_changed(e):
        try:
            slider_progreso.max = float(e.data)
            page.update()
        except: pass

    audio_player = ft.Audio(
        src="https://google.com", 
        autoplay=False,
        on_position_changed=on_position_changed,
        on_duration_changed=on_duration_changed
    )
    page.overlay.append(audio_player)

    # --- FUNCIONES ---
    def play_pause(e):
        if btn_play_pause.icon == ft.Icons.PLAY_ARROW:
            audio_player.resume()
            btn_play_pause.icon = ft.Icons.PAUSE
        else:
            audio_player.pause()
            btn_play_pause.icon = ft.Icons.PLAY_ARROW
        page.update()

    def descargar_cancion(e):
        v_id = e.control.data['id']
        titulo_limpio = "".join([c for c in e.control.data['titulo'] if c.isalnum() or c==' ']).strip()
        sb = ft.SnackBar(ft.Text(f"Bypass Download: {titulo_limpio}..."))
        page.overlay.append(sb)
        sb.open = True
        page.update()
        
        import yt_dlp
        url_descarga = f"https://www.youtube.com/watch?v={v_id}"
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]',
            'outtmpl': f'downloads/{titulo_limpio}.m4a',
            'quiet': True, 'nocheckcertificate': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url_descarga])
            sb.content = ft.Text("Coronamos: Archivo en /downloads ✅")
            sb.open = True
        except: pass
        page.update()

    def seleccionar_y_reproducir(e):
        v_id = e.control.data['id']
        # --- RESET DE BARRA (FIX BUG) ---
        slider_progreso.value = 0
        slider_progreso.visible = True
        controles_reproduccion.visible = True
        btn_play_pause.icon = ft.Icons.PAUSE
        page.update()
        
        try:
            audio_player.release() 
            url_directa = obtener_url_audio(v_id)
            audio_player.src = url_directa
            audio_player.update()
            audio_player.play()
        except: pass

    # --- BÚSQUEDA PREDICTIVA (ADIVINAR) ---
    def search_changed(e):
        query = e.data.lower()
        if not query:
            lista_sugerencias.visible = False
            page.update()
            return

        # Buscamos en historial + Intento de previsualización
        busquedas = obtener_historial()
        filtradas = [b for b in busquedas if query in b.lower()]
        
        # Si no hay en historial, dejamos el espacio para que el usuario complete
        if filtradas:
            lista_sugerencias.controls = [
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.HISTORY, size=16),
                    title=ft.Text(f, size=14), 
                    on_click=lambda x, val=f: aplicar_sugerencia(val),
                    dense=True
                ) for f in filtradas[:3]
            ]
            lista_sugerencias.visible = True
        else:
            lista_sugerencias.visible = False
        page.update()

    def aplicar_sugerencia(val):
        txt_busqueda.value = val
        lista_sugerencias.visible = False
        ejecutar_busqueda(None)

    # --- INTERFAZ ---
    txt_busqueda = ft.TextField(
        label="Busca tu música", 
        expand=True, 
        on_submit=lambda _: ejecutar_busqueda(None),
        on_change=search_changed,
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        border_radius=15,
        hint_text="Escribe algo..."
    )
    
    btn_buscar = ft.IconButton(
        icon=ft.Icons.PLAY_CIRCLE_FILL_ROUNDED, 
        icon_color="green",
        on_click=lambda _: ejecutar_busqueda(None),
        tooltip="Lanzar búsqueda"
    )
    
    lista_sugerencias = ft.Card(
        content=ft.Column(spacing=0),
        visible=False,
        elevation=5,
        margin=ft.margin.only(top=-10)
    )
    
    slider_progreso = ft.Slider(
        min=0, max=100, value=0, 
        on_change=lambda e: audio_player.seek(int(e.control.value)), 
        visible=False, active_color="green"
    )
    slider_progreso.active = False 

    btn_play_pause = ft.IconButton(icon=ft.Icons.PAUSE, on_click=play_pause, icon_size=40)
    
    controles_reproduccion = ft.Row(
        [
            ft.IconButton(ft.Icons.REPLAY_10, on_click=lambda _: audio_player.seek(max(0, audio_player.get_current_position()-10000))), 
            btn_play_pause, 
            ft.IconButton(ft.Icons.FORWARD_10, on_click=lambda _: audio_player.seek(audio_player.get_current_position()+10000))
        ],
        alignment=ft.MainAxisAlignment.CENTER, visible=False
    )

    lista_resultados = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)

    def ejecutar_busqueda(e):
        if not txt_busqueda.value: return
        guardar_en_historial(txt_busqueda.value)
        lista_sugerencias.visible = False
        lista_resultados.controls.clear()
        # Loader visual mientras busca para que no parezca que se congeló
        lista_resultados.controls.append(ft.ProgressBar(color="green"))
        page.update()
        
        try:
            # Ejecutamos búsqueda en un hilo para que la barra de música siga moviéndose
            def thread_search():
                canciones = buscar_cancion(txt_busqueda.value)
                lista_resultados.controls.clear()
                for c in canciones:
                    artista = "Desconocido"
                    if 'artists' in c and len(c['artists']) > 0:
                        artista = c['artists'][0]['name']
                    
                    img = c['thumbnails'][-1]['url']
                    lista_resultados.controls.append(
                        ft.ListTile(
                            leading=ft.Image(src=img, width=50, height=50, border_radius=5, fit=ft.ImageFit.COVER),
                            title=ft.Text(c['title'], max_lines=1, weight="bold"),
                            subtitle=ft.Text(artista),
                            on_click=seleccionar_y_reproducir,
                            data={'id': c['videoId']},
                            trailing=ft.IconButton(
                                ft.Icons.DOWNLOAD_ROUNDED, 
                                icon_color="blue",
                                on_click=descargar_cancion, 
                                data={'id': c['videoId'], 'titulo': c['title']}
                            ),
                        )
                    )
                page.update()
            
            threading.Thread(target=thread_search).start()
            
        except: pass

    page.add(
        ft.Column([
            ft.Row([txt_busqueda, btn_buscar]),
            lista_sugerencias,
        ]),
        slider_progreso,
        controles_reproduccion,
        ft.Divider(),
        lista_resultados
    )

if __name__ == "__main__":
    ft.app(target=main)
