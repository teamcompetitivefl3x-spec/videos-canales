# videos-canales

Sistema de producción y publicación automática de los canales de Charly:

| Canal | ID de YouTube | Conexión de Zapier (`connection_id`) | Para niños |
|---|---|---|---|
| **Pulso IA** (@pulsoia13) | UC2iTLuA6bWq6tBPKSf8u0AQ | `02f0f5e0-917a-894f-8297-9240089939e9` ("YouTube #2") | No |
| **Peque Planeta** (@pequeplaneta13) | UCbICcOOsaLr8k29VjItsvHw | `02384c5d-c711-81e9-82c5-87581476685a` ("YouTube") | **Sí** |

Todo es gratis: voz con Kokoro (open source), animación con PIL/numpy, música sintetizada, ffmpeg, GitHub como depósito temporal y Zapier (plan gratis: máx. 5 subidas a YouTube por día) para publicar.

## Estructura
- `pulso/`: motor de motion graphics de Pulso IA (`engine.py`), render (`render.py`), voz (`tts.py`), música (`music.py`), mezcla (`audio.py`) y escenas de ejemplo (`scenes.py` + `guion_ejemplo_klarna.md`).
- `infantil/`: Tula (tortuga) y Pipo (pajarito), escenario, objetos y escenas (`kids_render.py`), guion de ejemplo (`script.py`: contar del 1 al 10), voces (`tts_kids.py`), música y efectos (`kids_audio.py`) y miniatura (`thumb.py`).
- `marca/`: fotos de perfil y banners.
- `setup.sh`: instala dependencias, baja el modelo de voz y copia los scripts a las rutas fijas (`/home/claude/build` y `/home/claude/kids`).

## Flujo diario (lo ejecuta una tarea programada por canal)
1. `git clone --depth 1 https://github.com/teamcompetitivefl3x-spec/videos-canales /home/claude/videos-canales` (antes, `add_repo` con access "push") y `sh setup.sh`.
2. Investigar el tema con WebSearch y escribir un guion nuevo (no repetir temas: revisar `historial.md`).
3. Producir:
   - **Pulso IA**: reescribir `/home/claude/piloto/guion.md` (mismo formato que el ejemplo) y `/home/claude/build/scenes.py` (SCENES y un SHORT), y después `python3 tts.py em_alex`, render en 2 procesos (`render.py long em_alex F0 F1 partN.mp4`), unión y `python3 audio.py long`. Short: `render.py short em_alex 0` + `audio.py short 0`.
   - **Peque Planeta**: reescribir `/home/claude/kids/script.py` con el tema del día (mantener Tula y Pipo idénticos y agregar sprites o escenas en `kids_render.py` solo si hace falta), después `tts_kids.py`, `kids_audio.py` y render en 2 procesos más el Short (`kids_render.py short T0 T1 out.mp4 --title=...`).
4. Comprimir para subir: video largo con `-crf 26 -maxrate 2.5M -bufsize 5M` (objetivo < 45 MB) y Shorts con `-crf 24`. Nunca más de 90 MB por archivo.
5. Revisar fotogramas (abrirlos), duración (largo ≥ 8:00), audio y loudness (-14 a -15 LUFS).
6. Depósito temporal: rama `media` (rama huérfana, **force-push**, siempre con solo los archivos del día y nombres únicos con fecha). URL pública: `https://raw.githubusercontent.com/teamcompetitivefl3x-spec/videos-canales/media/<archivo>`. (La API de releases y el borrado de ramas están bloqueados en las sesiones de Claude; el force-push funciona).
7. Publicar con Zapier `YouTubeV4CLIAPI` → `upload_video` (tool_name `youtube_upload_video`) con el `connection_id` del canal: título, descripción (capítulos y fuentes), `tags`, `video` (URL raw), `thumbnail` (URL raw del .jpg 1280×720, < 2 MB), `privacy_status` "public", `made_for_kids` según el canal, `default_language`/`default_audio_language` "es", `notify_subscribers` "true". `publish_at` NO está disponible hasta entrar al Programa de Partners de YouTube.
8. Agregar una línea a `historial.md` (fecha · canal · título · ID del video) y hacer push a `main`.
9. Avisar a Charly con SendUserMessage: títulos, enlaces de YouTube y qué revisar.

## Reglas de contenido
- Español neutro (tú). Datos verificados con fuente y fecha. Nada de rumores ni copias de otros creadores.
- Pulso IA: noticias, historias reales, datos y curiosidades de IA; gancho en los primeros 15 s; 8:30–10:30.
- Peque Planeta: educativo para 2 a 6 años (números, colores, formas, animales, letras, cuentos), con pausas para que el niño responda; mínimo 8:00; cada episodio distinto de verdad (YouTube castiga el contenido infantil repetitivo).

## Ritmo y tope gratis (Zapier free: 100 tareas/mes, 2 por subida = 50 subidas/mes)
- Por canal, según el día del mes D y R = D % 6: R ∈ {1,3,5} → video largo · R ∈ {2,4} → Short · R = 0 → descanso.
- Tope: 25 subidas automáticas por canal y por mes (23 en 2026-11), contadas en `historial.md` (líneas marcadas "auto"). Si se llega al tope, ese día no se publica.
- Una sola llamada exitosa a Zapier por ejecución (la subida). Sin llamadas de verificación.
