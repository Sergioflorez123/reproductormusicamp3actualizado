import customtkinter as ctk
import pygame
from tkinter import filedialog
import threading
import time

# Clase para la lista doblemente enlazada
class Nodo:
    def __init__(self, cancion):
        self.cancion = cancion
        self.siguiente = None
        self.anterior = None

class ListaReproduccion:
    def __init__(self):
        self.primero = None
        self.ultimo = None
        self.actual = None
    
    def agregar_cancion(self, cancion):
        nuevo_nodo = Nodo(cancion)
        if not self.primero:
            self.primero = self.ultimo = self.actual = nuevo_nodo
        else:
            self.ultimo.siguiente = nuevo_nodo
            nuevo_nodo.anterior = self.ultimo
            self.ultimo = nuevo_nodo

    def siguiente_cancion(self):
        if self.actual and self.actual.siguiente:
            self.actual = self.actual.siguiente
            return self.actual.cancion
        return None

    def anterior_cancion(self):
        if self.actual and self.actual.anterior:
            self.actual = self.actual.anterior
            return self.actual.cancion
        return None

# Inicializar pygame mixer
pygame.mixer.init()
lista_reproduccion = ListaReproduccion()

def abrir_archivo():
    archivos = filedialog.askopenfilenames(filetypes=[("MP3 Files", "*.mp3")])
    for archivo in archivos:
        lista_reproduccion.agregar_cancion(archivo)
    actualizar_nombre()

def actualizar_nombre():
    if lista_reproduccion.actual:
        nombre_cancion.configure(text=lista_reproduccion.actual.cancion.split('/')[-1])

def reproducir():
    if lista_reproduccion.actual:
        pygame.mixer.music.load(lista_reproduccion.actual.cancion)
        pygame.mixer.music.play()
        actualizar_nombre()
        actualizar_barra_progreso()

def siguiente():
    cancion = lista_reproduccion.siguiente_cancion()
    if cancion:
        pygame.mixer.music.load(cancion)
        pygame.mixer.music.play()
        actualizar_nombre()
        actualizar_barra_progreso()

def anterior():
    cancion = lista_reproduccion.anterior_cancion()
    if cancion:
        pygame.mixer.music.load(cancion)
        pygame.mixer.music.play()
        actualizar_nombre()
        actualizar_barra_progreso()

def detener():
    pygame.mixer.music.stop()
    barra_progreso.set(0)

def pausar():
    pygame.mixer.music.pause()

def continuar():
    pygame.mixer.music.unpause()

def actualizar_barra_progreso():
    def actualizar():
        while pygame.mixer.music.get_busy():
            try:
                pos = pygame.mixer.music.get_pos() / 1000
                duracion = pygame.mixer.Sound(lista_reproduccion.actual.cancion).get_length()
                barra_progreso.set(pos / duracion)
                time.sleep(1)
            except:
                break
    threading.Thread(target=actualizar, daemon=True).start()

# Interfaz con customtkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.title("Reproductor de Música")
app.geometry("500x400")

frame = ctk.CTkFrame(app, fg_color="#1E1E1E")
frame.pack(pady=20, padx=20, fill="both", expand=True)

nombre_cancion = ctk.CTkLabel(frame, text="Selecciona una canción", font=("Arial", 16), text_color="white")
nombre_cancion.pack(pady=10)

barra_progreso = ctk.CTkProgressBar(frame, width=400, height=10)
barra_progreso.set(0)
barra_progreso.pack(pady=10)

boton_abrir = ctk.CTkButton(frame, text="Abrir", command=abrir_archivo, fg_color="#FF5733")
boton_abrir.pack()

boton_reproducir = ctk.CTkButton(frame, text="Reproducir", command=reproducir, fg_color="#33FF57")
boton_reproducir.pack()

boton_pausa = ctk.CTkButton(frame, text="Pausar", command=pausar, fg_color="#FFC300")
boton_pausa.pack()

boton_continuar = ctk.CTkButton(frame, text="Continuar", command=continuar, fg_color="#33A1FF")
boton_continuar.pack()

boton_detener = ctk.CTkButton(frame, text="Detener", command=detener, fg_color="#C70039")
boton_detener.pack()

boton_anterior = ctk.CTkButton(frame, text="Anterior", command=anterior, fg_color="#900C3F")
boton_anterior.pack()

boton_siguiente = ctk.CTkButton(frame, text="Siguiente", command=siguiente, fg_color="#581845")
boton_siguiente.pack()

app.mainloop()

