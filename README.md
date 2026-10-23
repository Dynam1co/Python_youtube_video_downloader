# Video Downloader

Aplicación para consultar videos de YouTube y guardar videos o audio. Incluye una interfaz web local y una versión de consola.

La interfaz web incluye [documentación del proyecto](http://127.0.0.1:5000/documentacion) y un [manual de uso](http://127.0.0.1:5000/manual).

## Uso de la interfaz web

1. Inicia la aplicación ejecutando `python web_app.py` desde la carpeta del proyecto y abre `http://127.0.0.1:5000` en el navegador.
2. Pega uno o varios enlaces de YouTube en el campo de texto. Para una descarga por lote, coloca cada enlace en una línea distinta.
3. Opcionalmente, pulsa **Consultar video** para ver el título, el canal y la duración del primer enlace. Al consultarlo también se cargan las calidades MP4 disponibles.
4. Elige **Video** o **Solo audio**. Para video, puedes dejar la calidad en automática o escoger una resolución disponible después de consultar el enlace.
5. Pulsa **Descargar ahora** y espera a que termine el proceso. El cuadro final muestra los archivos descargados, los errores que ocurrieron y un enlace **Ver archivo** para abrir cada resultado.

La interfaz guarda los videos en `downloads/video` y el audio en `downloads/audio` dentro del proyecto cuando la ruta definida en la configuración no está disponible. El audio se conserva en el formato original que ofrece YouTube, normalmente M4A. La calidad y los formatos disponibles dependen de cada video.

## Uso de la consola

La versión de consola se ejecuta con `python main.py` y presenta un menú:

- **Descargar enlace YouTube**: procesa un único enlace.
- **Descargar fichero**: lee enlaces desde un archivo de texto, uno por línea.
- **Salir**: termina el programa.

Después de elegir una de las dos primeras opciones, selecciona el tipo de descarga:

- **Descarga rápida video y audio**: obtiene el formato progresivo disponible, que incluye ambas pistas.
- **Descarga video seleccionando calidad**: muestra los formatos MP4 de video y permite escoger uno. Descarga el audio por separado y lo combina con el video.
- **Descarga audio**: descarga la pista de audio y la convierte a MP3.

La selección de calidad está disponible para un enlace individual. Al procesar un fichero, esa opción usa la primera calidad listada para cada enlace.

## Partes del programa

- [`web_app.py`](web_app.py): servidor Flask, consulta de información, selección de formatos, tareas de descarga y entrega de archivos al navegador. Usa `yt-dlp` y FFmpeg.
- [`templates/index.html`](templates/index.html): estructura de la interfaz web.
- [`static/app.js`](static/app.js): interacción de la página: consulta de enlaces, selección de formato, seguimiento del progreso y resultados.
- [`static/style.css`](static/style.css): estilos visuales de la interfaz.
- [`main.py`](main.py): menús y flujo de descarga de la versión de consola; usa `pytube` y `moviepy` para combinar pistas o convertir audio.
- [`config.py`](config.py) y [`conf_management.py`](conf_management.py): configuración y acceso a la ruta base de descargas usada por la consola. La interfaz web recurre a la carpeta `downloads` del proyecto cuando la ruta configurada no existe o no es válida en el sistema actual.
- `downloads/video` y `downloads/audio`: carpetas de salida usadas por la interfaz web como alternativa local.

## Notas de uso

- La interfaz web acepta enlaces de YouTube (`youtube.com` y `youtu.be`) y procesa las listas de forma secuencial.
- La vista previa consulta únicamente el primer enlace; la descarga puede incluir todos los enlaces pegados.
- Si un enlace falla, los demás enlaces de la tarea continúan procesándose y el resultado informa qué archivos tuvieron errores.
- Usa la herramienta solo con contenido que tengas derecho a descargar y de acuerdo con las condiciones aplicables de YouTube.

## Pruebas

Las pruebas individuales de validación y manejo de errores están en [`test/test_web_app.py`](test/test_web_app.py). Se ejecutan con:

```powershell
python -m unittest discover -s test -v
```
