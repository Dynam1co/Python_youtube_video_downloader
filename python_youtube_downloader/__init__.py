__version__ = '0.1.0'

from ast import Str
from pytube import YouTube
import os
from moviepy.editor import *


parent_dir = r"D:\Youtube"


def clear(): os.system('cls')


def menu_inicio() -> Str:
    clear()
    return input('Selecciona una opción:\n1. Descargar enlace YouTube\n2. Descargar fichero\n3. Salir\n\nOpción (1|2|3): ')


def seleccionar_accion() -> Str:
    return input('¿Qué deseas hacer?\n\n1. Descarga rápida vídeo y audio\n2. Descarga vídeo seleccionando calidad\n3. Descarga audio\n\nOpción (1|2|3): ')    


def print_proceso_terminado():
    print('Descarga completada')

    print('-------------------------------------------------------')


def pide_url() -> Str:
    return input('Url vídeo: ')


def procesa_fichero(ruta) -> list:
    list_enlaces = []

    file_object = open(ruta, 'r')

    [list_enlaces.append(linea) for linea in file_object]    

    file_object.close()

    return list_enlaces


def inicia_proceso_descarga(link, job, loop):
    contador = 1

    try:
        yt = YouTube(link)
    except:
        print('Error en el link: {0}'.format(link))
        return
    
    nombre_video = ''

    print('')
    print('-------------------------------------------------------')
    print('Título: {0}'.format(yt.title))
    print('Autor: {0}'.format(yt.author))    
    print('')

    video_y_audio = yt.streams.filter(progressive=True).order_by('resolution').desc().first()
    vids = yt.streams.filter(mime_type="video/mp4").order_by('resolution').desc()

    if job == '1':  # Vídeo y audio rápido
        video_y_audio.download(parent_dir + '/video')
        print_proceso_terminado()
    elif job == '3': # Solo audio
        ruta_fin = yt.streams.get_audio_only().download(parent_dir + '/audio')
        audioclip = AudioFileClip(ruta_fin)                
        audioclip.write_audiofile(audioclip.filename.replace('.mp4', '.mp3'))

        os.remove(audioclip.filename)

        print_proceso_terminado()
    elif job == '2':  # Descargar vídeo y audio seleccionando calidad    
        num_video_descargar = 1

        if not loop:
            print('')
            print('Seleccionar vídeo (1..{0})'.format(len(vids)))    

            for video in vids:
                print('    ({1}) - {0}'.format(video, contador))
                contador += 1

            print('')

            num_video_descargar = int(input('Nº vídeo: '))    

        num_video_descargar -= 1    

        nombre_video = vids[num_video_descargar].default_filename
        nombre_video_final = 'f_' + nombre_video
        vids[num_video_descargar].download(parent_dir + '/video')

        yt.streams.get_audio_only().download(parent_dir + '/audio')

        audioclip = AudioFileClip(parent_dir + '/audio/' + nombre_video)

        videoclip2 = VideoFileClip(parent_dir + '/video/' + nombre_video)
        videoclip2 = videoclip2.set_audio(audioclip)
        
        videoclip2.write_videofile(parent_dir + '/video/' + nombre_video_final)    

        os.remove(videoclip2.filename)
        os.remove(audioclip.filename)


if __name__ == "__main__":
    tarea = 0
    job = 0
    enlaces = []    

    while tarea != '3':        
        enlaces.clear()
        tarea = menu_inicio()
        loop = False

        clear()

        if tarea == '1':
            enlaces.append(pide_url())            
        elif tarea == '2':
            loop = True
            ruta_fichero = input('Ruta fichero enlaces: ')
            enlaces = procesa_fichero(ruta_fichero)        
        

        while job not in ['1', '2', '3']:
            clear()
            job = seleccionar_accion()

        [inicia_proceso_descarga(x, job, loop) for x in enlaces]

    print_proceso_terminado()