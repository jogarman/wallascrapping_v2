import tkinter as tk
from tkinter import ttk
from utils.utils import ciudades_espana
import subprocess
import os

class RedirectText(object):
    def __init__(self, text_widget):
        self.output = text_widget

    def write(self, string):
        self.output.configure(state='normal')  # Permitir escribir en el widget
        self.output.insert(tk.END, string)
        self.output.configure(state='disabled')  # Desactivar la escritura para el usuario
        self.output.see(tk.END)  # Desplazar el texto automáticamente hacia el final
        self.output.update_idletasks()  # SE SUPONE QUE ACTUALIZA LA VENTANA DE TEXTO CADA VEZ QUE ESCRIBES

    def flush(self):
        pass  # Método necesario para la compatibilidad con sys.stdout

class SearchItem:
    def __init__(self, item_name, municipio, estado, distancia, precio_minimo):
        self.item_name = item_name
        self.municipio = municipio
        self.estado = estado
        self.distancia = distancia
        self.precio_minimo = precio_minimo

    def __repr__(self):
        return (f"SearchItem(item_name='{self.item_name}', municipio='{self.municipio}', "
                f"estado='{self.estado}', distancia='{self.distancia}', precio_minimo='{self.precio_minimo}')")

def create_item_window(item_num, container):
    frame = ttk.Frame(container)
    frame.pack(side=tk.LEFT, padx=10, pady=10)

    tk.Label(frame, text=f"Item {item_num}:").pack(anchor=tk.W)
    item_entry = tk.Entry(frame)
    item_entry.insert(0, "iphone 14")
    item_entry.pack()

    tk.Label(frame, text="Municipios (pendiente):").pack(anchor=tk.W)
    municipio_var = tk.StringVar()
    municipio_combo = ttk.Combobox(frame, textvariable=municipio_var, values=list(ciudades_espana.keys()), state="readonly")
    municipio_combo.set("Madrid")
    municipio_combo.pack()

    tk.Label(frame, text="Estados:").pack(anchor=tk.W)
    state_var1 = tk.IntVar()
    state_var2 = tk.IntVar()
    state_var3 = tk.IntVar()

    def on_state_change(*args):
        check_search_button_state()

    state_var1.trace_add("write", on_state_change)
    state_var2.trace_add("write", on_state_change)
    state_var3.trace_add("write", on_state_change)

    tk.Checkbutton(frame, text="new", variable=state_var1).pack(anchor=tk.W)
    tk.Checkbutton(frame, text="as_good_as_new", variable=state_var2).pack(anchor=tk.W)
    tk.Checkbutton(frame, text="good", variable=state_var3).pack(anchor=tk.W)

    tk.Label(frame, text="Distancia km: (2000 para todo españa)").pack(anchor=tk.W)
    distance_entry = tk.Entry(frame)
    distance_entry.insert(0, "60")
    distance_entry.pack()

    tk.Label(frame, text="Precio mínimo €:").pack(anchor=tk.W)
    min_price_entry = tk.Entry(frame)
    min_price_entry.insert(0, "250")
    min_price_entry.pack()

    item_data.append({
        "item": item_entry,
        "municipios": municipio_combo,
        "estados": [state_var1, state_var2, state_var3],
        "distancia": distance_entry,
        "precio_minimo": min_price_entry
    })

def on_next_button_click():
    for widget in container.winfo_children():
        widget.destroy()

    num_items = int(combo.get())
    global item_data
    item_data = []

    for i in range(1, num_items + 1):
        create_item_window(i, container)

    search_button.pack(side=tk.BOTTOM, pady=10)

def check_search_button_state():
    for item in item_data:
        estados_seleccionados = any(var.get() for var in item["estados"])
        municipio_seleccionado = bool(item["municipios"].get())
        
        if not (estados_seleccionados and municipio_seleccionado):
            search_button.config(state=tk.DISABLED)
            return
    search_button.config(state=tk.NORMAL)

def on_search_button_click():
    search_items = []

    for item in item_data:
        item_name = item["item"].get()
        municipio = item["municipios"].get()
        estados = [var.get() for var in item["estados"]]
        distancia = item["distancia"].get()
        precio_minimo = item["precio_minimo"].get()

        estado_labels = ['new', 'as_good_as_new', 'good']
        for idx, selected in enumerate(estados):
            if selected:
                estado = estado_labels[idx]  # Define estado aquí
                search_item = SearchItem(
                    item_name='"' + item_name + '"',
                    municipio=municipio,
                    estado=estado,
                    distancia=distancia,
                    precio_minimo=precio_minimo
                )
                search_items.append(search_item)
                print(f"Wallascrapeando item: {idx}")
                print(search_item)
                run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)


def run_wallascrap(item_name, municipio, estado, distancia, precio_minimo):
    print("def run_wallascrap...")
    python_executable = os.path.join('.env', 'Scripts', 'python.exe')
    command = [
        python_executable, '01_wallascrap.py',
        '--item_name', item_name,
        '--municipio', municipio,
        '--estado', estado,
        '--distancia', str(distancia),
        '--precio_minimo', str(precio_minimo)
    ]
    print("command: ", command)
    result = subprocess.run(command, capture_output=True, text=True)
    # Mostrar la salida en el widget de texto
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

# Creo archivo con el output

import sys
import os
from datetime import datetime

# Crear ventana principal
root = tk.Tk()
root.title("wallascrap")

container = ttk.Frame(root)

tk.Label(root, text="Número de items a buscar:").pack(anchor=tk.W)
combo = ttk.Combobox(root, values=[1, 2, 3, 4], state="readonly")
combo.pack()
combo.current(0)

next_button = ttk.Button(root, text="Siguiente...", command=on_next_button_click)
next_button.pack(pady=10)

container.pack()

search_button = ttk.Button(root, text="Buscar", command=on_search_button_click)
search_button.config(state=tk.DISABLED)

item_data = []

"""
# Añadir el cuadro de texto para la salida
output_text = tk.Text(root, wrap='word', state='disabled', height=10, width=50)
output_text.pack(pady=10)
# Redirigir sys.stdout a nuestro cuadro de texto
sys.stdout = RedirectText(output_text)
"""
root.mainloop()
