import customtkinter as ctk
import pygame
from tkinter import filedialog, simpledialog

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
    
    def agregar_cancion_inicio(self, cancion):
        nuevo_nodo = Nodo(cancion)
        if not self.primero:
            self.primero = self.ultimo = self.actual = nuevo_nodo
        else:
            nuevo_nodo.siguiente = self.primero
            self.primero.anterior = nuevo_nodo
            self.primero = nuevo_nodo

    def agregar_cancion_final(self, cancion):
        nuevo_nodo = Nodo(cancion)
        if not self.primero:
            self.primero = self.ultimo = self.actual = nuevo_nodo
        else:
            self.ultimo.siguiente = nuevo_nodo
            nuevo_nodo.anterior = self.ultimo
            self.ultimo = nuevo_nodo

    def agregar_cancion_posicion(self, cancion, posicion):
        if posicion == 0:
            self.agregar_cancion_inicio(cancion)
            return
        nuevo_nodo = Nodo(cancion)
        temp = self.primero
        for _ in range(posicion - 1):
            if temp is None or temp.siguiente is None:
                self.agregar_cancion_final(cancion)
                return
            temp = temp.siguiente
        nuevo_nodo.siguiente = temp.siguiente
        nuevo_nodo.anterior = temp
        if temp.siguiente:
            temp.siguiente.anterior = nuevo_nodo
        temp.siguiente = nuevo_nodo

    def eliminar_cancion(self):
        if self.actual:
            if self.actual == self.primero:
                self.primero = self.primero.siguiente
                if self.primero:
                    self.primero.anterior = None
            elif self.actual == self.ultimo:
                self.ultimo = self.ultimo.anterior
                if self.ultimo:
                    self.ultimo.siguiente = None
            else:
                self.actual.anterior.siguiente = self.actual.siguiente
                self.actual.siguiente.anterior = self.actual.anterior
            self.actual = self.primero
    
    def eliminar_cancion_por_posicion(self, posicion):
        if not self.primero:
            return
        temp = self.primero
        if posicion == 0:
            self.primero = temp.siguiente
            if self.primero:
                self.primero.anterior = None
            return
        for _ in range(posicion):
            temp = temp.siguiente
            if temp is None:
                return
        if temp.siguiente:
            temp.siguiente.anterior = temp.anterior
        if temp.anterior:
            temp.anterior.siguiente = temp.siguiente
        if temp == self.ultimo:
            self.ultimo = temp.anterior
    
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

# Funciones del reproductor
def abrir_archivo():
    archivos = filedialog.askopenfilenames(filetypes=[("MP3 Files", "*.mp3")])
    for archivo in archivos:
        lista_reproduccion.agregar_cancion_final(archivo)
    actualizar_nombre()

def actualizar_nombre():
    if lista_reproduccion.actual:
        nombre_cancion.configure(text=lista_reproduccion.actual.cancion.split('/')[-1])

def reproducir():
    if lista_reproduccion.actual:
        pygame.mixer.music.load(lista_reproduccion.actual.cancion)
        pygame.mixer.music.play()

def siguiente():
    cancion = lista_reproduccion.siguiente_cancion()
    if cancion:
        pygame.mixer.music.load(cancion)
        pygame.mixer.music.play()
        actualizar_nombre()

def anterior():
    cancion = lista_reproduccion.anterior_cancion()
    if cancion:
        pygame.mixer.music.load(cancion)
        pygame.mixer.music.play()
        actualizar_nombre()

def detener():
    pygame.mixer.music.stop()

def pausar():
    pygame.mixer.music.pause()

def continuar():
    pygame.mixer.music.unpause()

def agregar_posicion():
    cancion = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
    if cancion:
        posicion = simpledialog.askinteger("Posición", "Ingrese la posición:")
        if posicion is not None:
            lista_reproduccion.agregar_cancion_posicion(cancion, posicion)

def eliminar_posicion():
    posicion = simpledialog.askinteger("Posición", "Ingrese la posición a eliminar:")
    if posicion is not None:
        lista_reproduccion.eliminar_cancion_por_posicion(posicion)

# Interfaz con customtkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Reproductor de Música")
app.geometry("500x400")

frame = ctk.CTkFrame(app)
frame.pack(pady=20, padx=20, fill="both", expand=True)

nombre_cancion = ctk.CTkLabel(frame, text="Selecciona una canción", font=("Arial", 16))
nombre_cancion.pack(pady=10)

boton_abrir = ctk.CTkButton(frame, text="Abrir", command=abrir_archivo)
boton_abrir.pack()

boton_reproducir = ctk.CTkButton(frame, text="Reproducir", command=reproducir)
boton_reproducir.pack()

boton_pausa = ctk.CTkButton(frame, text="Pausar", command=pausar)
boton_pausa.pack()

boton_continuar = ctk.CTkButton(frame, text="Continuar", command=continuar)
boton_continuar.pack()

boton_detener = ctk.CTkButton(frame, text="Detener", command=detener)
boton_detener.pack()

boton_anterior = ctk.CTkButton(frame, text="Anterior", command=anterior)
boton_anterior.pack()

boton_siguiente = ctk.CTkButton(frame, text="Siguiente", command=siguiente)
boton_siguiente.pack()

boton_agregar_posicion = ctk.CTkButton(frame, text="Agregar en posición", command=agregar_posicion)
boton_agregar_posicion.pack()

boton_eliminar_posicion = ctk.CTkButton(frame, text="Eliminar en posición", command=eliminar_posicion)
boton_eliminar_posicion.pack()

app.mainloop()






































