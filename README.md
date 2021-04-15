# Python Youtube downloader 📺

Created: Sep 25, 2020 6:20 PM

Descarga de vídeos de Youtube seleccionando la calidad. También se puede descargar solo el audio de un vídeo.

## Pre-requisitos 📋

- Entorno virtual con las dependencias instaladas del fichero [requirements.txt](requirements.txt)

## Configuraciones ⚙️

Configurar la ruta donde se descargarán los vídeos:

En el fichero [config.py](python_youtube_downloader/config.py) cambiaremos la ruta que viene por defecto.

## Herramientas/Librerías usadas 🛠️

Estas son las herramientas usadas durante el desarrollo del proyecto:

- [NeoVim](https://neovim.io/): Como editor de código Python.
- [Pytube 9.6.0](https://python-pytube.readthedocs.io/en/latest/): Para descarga de vídeos de Youtube.
- [moviepy](https://pypi.org/project/moviepy/): Para montar el audio y el vídeo en un mismo fichero.

## Funcionamiento 🔧

Podemos descargar los vídeos uno a uno usando su link a Youtube o poner las urls en un fichero de texto y que la aplicación los descargue en bucle.

Al iniciar la aplicación nos pide que seleccionemos una de las dos opciones:

![Python%20Youtube%20downloader%20950958136b7941818d625833951a1a95/Capture.png](Python%20Youtube%20downloader%20950958136b7941818d625833951a1a95/Capture.png)

### Descarga un solo link

Nos pedirá la url del vídeo:

![Python%20Youtube%20downloader%20950958136b7941818d625833951a1a95/Capture%201.png](Python%20Youtube%20downloader%20950958136b7941818d625833951a1a95/Capture%201.png)

Ahora tendremos que seleccionar una de estas tres opciones:

- Descarga rápida de vídeo y audio: descarga el vídeo junto con el audio en baja calidad
- Descargar vídeo seleccionando la calidad: nos mostrará las calidades disponibles en el vídeo para que seleccionemos una. Esta opción es la que más tarda porque tiene que descargar el vídeo por un lado y el audio por otro para mergearlo después. Este proceso es transparente para el usuario y se hace de forma automática.
- Descargar audio: descarga únicamente el audio de la canción.

![Python%20Youtube%20downloader%20950958136b7941818d625833951a1a95/Capture%202.png](Python%20Youtube%20downloader%20950958136b7941818d625833951a1a95/Capture%202.png)

### Descarga en bucle

Nos pedirá la ruta del fichero de texto que contiene los enlaces:

![Python%20Youtube%20downloader%20950958136b7941818d625833951a1a95/Capture%203.png](Python%20Youtube%20downloader%20950958136b7941818d625833951a1a95/Capture%203.png)

El fichero tendrá este formato:

![Python%20Youtube%20downloader%20950958136b7941818d625833951a1a95/Capture%204.png](Python%20Youtube%20downloader%20950958136b7941818d625833951a1a95/Capture%204.png)

Cuando el proceso acabe, veremos los vídeos o audios en la ruta configurada.

## Expresiones de gratitud 🎁

- Comenta a otros sobre este proyecto 📢
- Da las gracias públicamente 🤓
- Sígueme en [Twitter](https://twitter.com/AsensiFj) 🐦