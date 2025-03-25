from tkinter import Button, Label, Tk, filedialog, ttk, Frame, Listbox, Scrollbar, messagebox, simpledialog
from tkinter.font import Font
import pygame
import mutagen
from mutagen.mp3 import MP3
import os
import time

class Nodo:
    def __init__(self, cancion):
        self.cancion = cancion
        self.siguiente = None
        self.anterior = None

class ListaDoble:
    def __init__(self):
        self.primero = None
        self.ultimo = None
        self.actual = None
        self.tamano = 0

    def esta_vacia(self):
        return self.primero is None

    def agregar_inicio(self, cancion):
        nuevo_nodo = Nodo(cancion)
        if self.esta_vacia():
            self.primero = self.ultimo = self.actual = nuevo_nodo
        else:
            nuevo_nodo.siguiente = self.primero
            self.primero.anterior = nuevo_nodo
            self.primero = nuevo_nodo
        self.tamano += 1

    def agregar_final(self, cancion):
        nuevo_nodo = Nodo(cancion)
        if self.esta_vacia():
            self.primero = self.ultimo = self.actual = nuevo_nodo
        else:
            self.ultimo.siguiente = nuevo_nodo
            nuevo_nodo.anterior = self.ultimo
            self.ultimo = nuevo_nodo
        self.tamano += 1

    def agregar_posicion(self, cancion, posicion):
        if posicion <= 0:
            self.agregar_inicio(cancion)
        elif posicion >= self.tamano:
            self.agregar_final(cancion)
        else:
            nuevo_nodo = Nodo(cancion)
            temp = self.primero
            for _ in range(posicion - 1):
                temp = temp.siguiente
            nuevo_nodo.siguiente = temp.siguiente
            nuevo_nodo.anterior = temp
            temp.siguiente.anterior = nuevo_nodo
            temp.siguiente = nuevo_nodo
            self.tamano += 1

    def eliminar(self, cancion):
        temp = self.primero
        while temp:
            if temp.cancion == cancion:
                if temp.anterior:
                    temp.anterior.siguiente = temp.siguiente
                else:
                    self.primero = temp.siguiente
                if temp.siguiente:
                    temp.siguiente.anterior = temp.anterior
                else:
                    self.ultimo = temp.anterior
                
                if temp == self.actual:
                    self.actual = self.primero
                
                self.tamano -= 1
                return True
            temp = temp.siguiente
        return False

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

    def obtener_lista(self):
        canciones = []
        temp = self.primero
        while temp:
            canciones.append(temp.cancion)
            temp = temp.siguiente
        return canciones

    def obtener_duracion(self, cancion):
        try:
            audio = MP3(cancion)
            return audio.info.length
        except:
            return 0

# Configuración inicial
lista_reproduccion = ListaDoble()
pygame.mixer.init()

# Funciones del reproductor
def actualizar_info():
    if lista_reproduccion.esta_vacia():
        info_cancion.config(text="No hay canciones en la lista")
    else:
        info_cancion.config(text=f"{lista_reproduccion.tamano} canciones en la lista")

def actualizar_resaltado():
    if lista_reproduccion.actual:
        canciones = lista_reproduccion.obtener_lista()
        try:
            indice = canciones.index(lista_reproduccion.actual.cancion)
            lista_canciones.selection_clear(0, 'end')
            lista_canciones.selection_set(indice)
            lista_canciones.see(indice)
        except ValueError:
            pass

def abrir_archivo(posicion):
    archivos = filedialog.askopenfilenames(filetypes=[('Archivos MP3', '*.mp3')])
    if archivos:
        for archivo in archivos:
            nombre_cancion = os.path.basename(archivo)
            if posicion == 'inicio':
                lista_reproduccion.agregar_inicio(archivo)
                lista_canciones.insert(0, nombre_cancion)
            else:  # 'final'
                lista_reproduccion.agregar_final(archivo)
                lista_canciones.insert('end', nombre_cancion)
        actualizar_info()

def agregar_en_posicion():
    archivo = filedialog.askopenfilename(filetypes=[('Archivos MP3', '*.mp3')])
    if archivo:
        posicion = simpledialog.askinteger("Posición", "Ingrese la posición donde insertar:")
        if posicion is not None:
            nombre_cancion = os.path.basename(archivo)
            lista_reproduccion.agregar_posicion(archivo, posicion)
            lista_canciones.insert(posicion, nombre_cancion)
            actualizar_info()

def eliminar_cancion():
    seleccion = lista_canciones.curselection()
    if seleccion:
        cancion = lista_canciones.get(seleccion)
        canciones = lista_reproduccion.obtener_lista()
        for c in canciones:
            if os.path.basename(c) == cancion:
                lista_reproduccion.eliminar(c)
                break
        lista_canciones.delete(seleccion)
        actualizar_info()
    else:
        messagebox.showwarning("Advertencia", "Seleccione una canción para eliminar")

def reproducir_cancion_actual():
    global pausado, tiempo_inicio, duracion_total
    
    if lista_reproduccion.actual:
        cancion = lista_reproduccion.actual.cancion
        pygame.mixer.music.load(cancion)
        pygame.mixer.music.play()
        pausado = False
        estado_reproduccion.config(text="Reproduciendo")
        
        nombre_cancion = os.path.basename(cancion)
        info_cancion.config(text=f"Reproduciendo: {nombre_cancion}")
        
        duracion_total = lista_reproduccion.obtener_duracion(cancion)
        tiempo_inicio = time.time()
        progress_bar['maximum'] = duracion_total
        progress_bar['value'] = 0
        
        actualizar_resaltado()
        actualizar_barra_progreso()
        
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
        ventana.after(100, verificar_fin_cancion)

def verificar_fin_cancion():
    for event in pygame.event.get():
        if event.type == pygame.USEREVENT:
            adelantar_cancion()
    ventana.after(100, verificar_fin_cancion)

def actualizar_barra_progreso():
    if pygame.mixer.music.get_busy() and not pausado:
        tiempo_transcurrido = time.time() - tiempo_inicio
        progress_bar['value'] = min(tiempo_transcurrido, duracion_total)
        ventana.after(1000, actualizar_barra_progreso)

def toggle_play():
    global pausado, tiempo_inicio, duracion_total
    
    if lista_reproduccion.esta_vacia():
        messagebox.showwarning("Advertencia", "La lista de reproducción está vacía")
        return
    
    if pygame.mixer.music.get_busy() and not pausado:
        pygame.mixer.music.pause()
        pausado = True
        estado_reproduccion.config(text="Pausado")
    elif pausado:
        pygame.mixer.music.unpause()
        pausado = False
        estado_reproduccion.config(text="Reproduciendo")
        actualizar_barra_progreso()
    else:
        reproducir_cancion_actual()

def adelantar_cancion():
    if lista_reproduccion.esta_vacia():
        messagebox.showwarning("Advertencia", "No hay canciones en la lista")
        return
    
    cancion = lista_reproduccion.siguiente_cancion()
    if cancion:
        reproducir_cancion_actual()
    else:
        # Si no hay siguiente canción, volver al inicio
        lista_reproduccion.actual = lista_reproduccion.primero
        if lista_reproduccion.actual:
            reproducir_cancion_actual()
            messagebox.showinfo("Información", "Volviendo al inicio de la lista")
        else:
            detener()

def retroceder_cancion():
    if lista_reproduccion.esta_vacia():
        messagebox.showwarning("Advertencia", "No hay canciones en la lista")
        return
    
    cancion = lista_reproduccion.anterior_cancion()
    if cancion:
        reproducir_cancion_actual()
    else:
        # Si no hay canción anterior, ir al final
        lista_reproduccion.actual = lista_reproduccion.ultimo
        if lista_reproduccion.actual:
            reproducir_cancion_actual()
            messagebox.showinfo("Información", "Yendo al final de la lista")
        else:
            detener()

def detener():
    pygame.mixer.music.stop()
    estado_reproduccion.config(text="Detenido")
    progress_bar['value'] = 0

def on_double_click(event):
    seleccion = lista_canciones.curselection()
    if seleccion:
        canciones = lista_reproduccion.obtener_lista()
        cancion_seleccionada = lista_canciones.get(seleccion)
        for i, cancion in enumerate(canciones):
            if os.path.basename(cancion) == cancion_seleccionada:
                temp = lista_reproduccion.primero
                for _ in range(i):
                    temp = temp.siguiente
                lista_reproduccion.actual = temp
                reproducir_cancion_actual()
                break

# Crear ventana principal
ventana = Tk()
ventana.title('Reproductor de Música Avanzado')
ventana.config(bg='#1E3F66')
ventana.geometry('650x550')
ventana.resizable(0, 0)

# Fuentes personalizadas
titulo_font = Font(family='Helvetica', size=16, weight='bold')
boton_font = Font(family='Arial', size=10)
lista_font = Font(family='Arial', size=10)

# Frame principal
main_frame = Frame(ventana, bg='#1E3F66')
main_frame.pack(fill='both', expand=True, padx=10, pady=10)

# Título
Label(main_frame, text='Reproductor de Música', font=titulo_font, 
      bg='#1a1a1a', fg='white').pack(pady=(0, 10))

# Frame para controles superiores
control_frame = Frame(main_frame, bg='#1E3F66')
control_frame.pack(fill='x', pady=(0, 10))

# Botones de control (agregar/eliminar)
Button(control_frame, text='Agregar al inicio', command=lambda: abrir_archivo('inicio'), 
       font=boton_font, bg='#333', fg='white', relief='flat').pack(side='left', padx=2)
Button(control_frame, text='Agregar al final', command=lambda: abrir_archivo('final'), 
       font=boton_font, bg='#333', fg='white', relief='flat').pack(side='left', padx=2)
Button(control_frame, text='Agregar en posición', command=agregar_en_posicion, 
       font=boton_font, bg='#333', fg='white', relief='flat').pack(side='left', padx=2)
Button(control_frame, text='Eliminar', command=eliminar_cancion, 
       font=boton_font, bg='#ff3333', fg='white', relief='flat').pack(side='left', padx=2)

# Frame para la lista de reproducción
lista_frame = Frame(main_frame, bg='#1a1a1a')
lista_frame.pack(fill='both', expand=True)

# Scrollbar
scrollbar = Scrollbar(lista_frame)
scrollbar.pack(side='right', fill='y')

# Lista de canciones
lista_canciones = Listbox(lista_frame, width=70, height=15, bg='#333', fg='white', 
                          selectbackground='#4d4d4d', font=lista_font, 
                          yscrollcommand=scrollbar.set)
lista_canciones.pack(fill='both', expand=True)
scrollbar.config(command=lista_canciones.yview)

# Frame para controles de reproducción
reproductor_frame = Frame(main_frame, bg='#1a1a1a')
reproductor_frame.pack(fill='x', pady=(10, 0))

# Información de la canción actual
info_cancion = Label(reproductor_frame, text='No hay canción seleccionada', 
                     bg='#1a1a1a', fg='white', font=boton_font)
info_cancion.pack()

# Barra de progreso
progress_bar = ttk.Progressbar(reproductor_frame, orient='horizontal', 
                              mode='determinate', length=450)
progress_bar.pack(pady=5)

# Frame para botones de navegación
nav_frame = Frame(reproductor_frame, bg='#1a1a1a')
nav_frame.pack()

# Botones de navegación (mejor organizados)
Button(nav_frame, text='⏮ Anterior', command=retroceder_cancion, 
       font=boton_font, bg='#555', fg='white', relief='flat', width=10).pack(side='left', padx=5)
Button(nav_frame, text='⏯ Play/Pausa', command=toggle_play, 
       font=boton_font, bg='#4CAF50', fg='white', relief='flat', width=10).pack(side='left', padx=5)
Button(nav_frame, text='⏹ Detener', command=detener, 
       font=boton_font, bg='#555', fg='white', relief='flat', width=10).pack(side='left', padx=5)
Button(nav_frame, text='⏭ Siguiente', command=adelantar_cancion, 
       font=boton_font, bg='#555', fg='white', relief='flat', width=10).pack(side='left', padx=5)

# Estado de reproducción
estado_reproduccion = Label(reproductor_frame, text='Detenido', 
                           bg='#1a1a1a', fg='white', font=boton_font)
estado_reproduccion.pack(side='left', padx=10)

# Configurar evento para doble clic
lista_canciones.bind('<Double-Button-1>', on_double_click)

# Variables globales
pausado = False
tiempo_inicio = 0
duracion_total = 0

# Inicializar
actualizar_info()

# Ejecutar ventana
ventana.mainloop()