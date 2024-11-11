import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from logic.subnet_calculator import SubnetCalculator
from gui.subnet_visualizer import SubnetVisualizer
import ipaddress
import requests
import random
import logging
import tkinter.font

class APIClient:
    def __init__(self):
        self.base_url = "http://localhost:5000"  # Asegúrate de que este puerto sea correcto

    def validate_ip_and_mask(self, ip_address, subnet_mask):
        try:
            response = requests.get(f"{self.base_url}/validate", params={
                "ip": ip_address,
                "mask": subnet_mask
            })
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error al validar IP y máscara: {e}")
            return {"valid": False, "error": str(e)}

    def get_examples(self):
        try:
            response = requests.get(f"{self.base_url}/examples")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error al obtener ejemplos: {e}")
            return {"examples": []}

class SubnetCalculatorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Calculadora de Subredes Avanzada")
        # Hacer que la ventana ocupe toda la pantalla
        master.state('zoomed')
        self.calculator = SubnetCalculator()
        self.resultados = None  # Inicializar resultados
        self.api_client = APIClient()
        
        # Crear un marco principal
        self.main_frame = ttk.Frame(master)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Crear un canvas
        self.canvas = tk.Canvas(self.main_frame)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Agregar barras de desplazamiento
        self.scrollbar_y = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.scrollbar_x = ttk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scrollbar_x.grid(row=1, column=0, sticky="ew")

        # Configurar el canvas
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        self.canvas.bind('<Configure>', self.on_canvas_configure)

        # Crear el marco interno
        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # Configurar el desplazamiento con la rueda del ratón
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Hacer que las filas y columnas se expandan
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.create_widgets()

    def on_canvas_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # Asegurar que el ancho del canvas sea al menos el ancho de la ventana
        self.canvas.itemconfig(self.canvas_frame, width=max(self.inner_frame.winfo_reqwidth(), event.width))

    def create_widgets(self):
        # Aumentar el padding y el tamaño de fuente para mejorar la visualización
        style = ttk.Style()
        style.configure("TLabel", padding=5, font=('Helvetica', 12))
        style.configure("TEntry", padding=5, font=('Helvetica', 12))
        style.configure("TButton", padding=5, font=('Helvetica', 12))

        self.ip_label = ttk.Label(self.inner_frame, text="Dirección IP:")
        self.ip_entry = ttk.Entry(self.inner_frame, width=30)
        self.ip_entry.grid(row=0, column=1, padx=10, pady=5)
        self.ip_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")

        self.mask_label = ttk.Label(self.inner_frame, text="Máscara de subred (CIDR):")
        self.mask_entry = ttk.Entry(self.inner_frame, width=30)
        self.mask_entry.grid(row=1, column=1, padx=10, pady=5)
        self.mask_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")

        self.subnets_label = ttk.Label(self.inner_frame, text="Número de subredes:")
        self.subnets_entry = ttk.Entry(self.inner_frame, width=30)
        self.subnets_entry.grid(row=2, column=1, padx=10, pady=5)
        self.subnets_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")

        # Mover el botón de guía a la parte superior
        self.guide_button = ttk.Button(self.inner_frame, text="Mostrar Guía de Subnetting", command=self.show_guide)
        self.guide_button.grid(row=0, column=2, padx=10, pady=5, sticky="e")

        self.calculate_button = ttk.Button(self.inner_frame, text="Calcular", command=self.calculate)
        self.calculate_button.grid(row=3, column=0, columnspan=2, pady=20)

        # Agregar un botón para validar la IP y la máscara
        self.validate_button = ttk.Button(self.inner_frame, text="Validar IP y Máscara", command=self.validate_ip_and_mask)
        self.validate_button.grid(row=3, column=1, padx=10, pady=5, sticky="e")

        # Agregar un botón para obtener ejemplos
        self.examples_button = ttk.Button(self.inner_frame, text="Obtener Ejemplos", command=self.get_examples)
        self.examples_button.grid(row=3, column=2, padx=10, pady=5, sticky="e")

        # Modificar la creación de las tablas para que muestren los encabezados
        table_width = 1000  # Ancho total de la tabla

        self.result_tree = ttk.Treeview(self.inner_frame, columns=("Número", "Red", "Primera IP", "Última IP", "Broadcast"), show="headings", height=10)
        for col in self.result_tree["columns"]:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=table_width // 5)
        self.result_tree.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        self.binary_tree = ttk.Treeview(self.inner_frame, columns=("Número", "Red", "Binario"), show="headings", height=10)
        for col in self.binary_tree["columns"]:
            self.binary_tree.heading(col, text=col)
            self.binary_tree.column(col, width=table_width // 3)
        self.binary_tree.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        self.device_tree = ttk.Treeview(self.inner_frame, columns=("Tipo", "Nombre", "Interfaz", "IP", "Máscara", "Gateway"), show="headings", height=10)
        for col in self.device_tree["columns"]:
            self.device_tree.heading(col, text=col)
            self.device_tree.column(col, width=table_width // 6)
        self.device_tree.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        self.visualizer = SubnetVisualizer(self.inner_frame)
        self.visualizer.frame.grid(row=7, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        self.show_ips_button = ttk.Button(self.inner_frame, text="Mostrar IPs utilizables", command=self.show_usable_ips)
        self.show_ips_button.grid(row=8, column=0, columnspan=2, pady=20)

        self.ip_list_text = tk.Text(self.inner_frame, height=15, width=80, font=('Helvetica', 10))
        self.ip_list_text.grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.ip_class_label = ttk.Label(self.inner_frame, text="Clase de IP:", font=('Helvetica', 14, 'bold'))
        self.ip_class_label.grid(row=10, column=0, columnspan=2, padx=10, pady=10)

        # Hacer que las filas y columnas se expandan
        for i in range(11):
            self.inner_frame.grid_rowconfigure(i, weight=1)
        for i in range(3):
            self.inner_frame.grid_columnconfigure(i, weight=1)

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    

    def calculate(self):
        try:
            ip_address = self.ip_entry.get().strip()
            subnet_mask = int(self.mask_entry.get().strip())
            num_subnets = int(self.subnets_entry.get().strip())

            if not 0 <= subnet_mask <= 32:
                raise ValueError("La máscara de subred debe estar entre 0 y 32.")

            # Modificar esta parte para usar strict=False
            network = ipaddress.IPv4Network(f"{ip_address}/{subnet_mask}", strict=False)

            # Calcular el nuevo prefijo basado en el número de subredes solicitadas
            new_prefix = network.prefixlen + max(0, (num_subnets - 1).bit_length())
            if new_prefix > 32:
                raise ValueError("No es posible crear tantas subredes con esta máscara.")

            # Aumentar el límite de recursión para manejar redes grandes
            import sys
            sys.setrecursionlimit(10000)

            result = self.calculator.calculate_subnets(str(network.network_address), subnet_mask, num_subnets)

            self.resultados = result
            self.display_result(result)
            self.visualizer.draw_subnets(result['subnets'])

            # Mostrar la clase de IP
            ip_class = self.calculator.determine_ip_class(ip_address)
            self.ip_class_label.config(text=f"Clase de IP: {ip_class}")

        except ValueError as e:
            self.show_error(str(e))
        except RecursionError:
            self.show_error("La red es demasiado grande para calcular. Intente con una red más pequeña o menos subredes.")
        except Exception as e:
            self.show_error(f"Ocurrió un error inesperado: {str(e)}")

    def obtener_resultados(self):
        return self.resultados

    def display_result(self, result):
        self.result_tree.delete(*self.result_tree.get_children())
        self.binary_tree.delete(*self.binary_tree.get_children())
        self.device_tree.delete(*self.device_tree.get_children())

        for i, subnet in enumerate(result['subnets'], 1):
            self.result_tree.insert("", "end", values=(
                i,
                subnet['network'],
                subnet['first_ip'],
                subnet['last_ip'],
                subnet['broadcast']
            ))

            binary_network = bin(int(ipaddress.IPv4Address(subnet['network'])))[2:].zfill(32)
            self.binary_tree.insert("", "end", values=(
                i,
                subnet['network'],
                binary_network
            ))

        # Mostrar todos los dispositivos posibles
        self.device_tree.insert("", "end", values=("Router", "Router Principal", "eth0", result['network'], result['netmask'], "N/A"))
        for i, subnet in enumerate(result['subnets'], 1):
            network = ipaddress.IPv4Network(f"{subnet['network']}/{subnet['netmask']}", strict=False)
            usable_ips = list(network.hosts())
            
            if usable_ips:
                # Agregar switch para cada subred
                self.device_tree.insert("", "end", values=("Switch", f"Switch-{i}", f"eth0", str(usable_ips[0]), subnet['netmask'], subnet['first_ip']))
                
                # Agregar PCs para cada subred (máximo 3 por subred para no sobrecargar la vista)
                for j, ip in enumerate(usable_ips[1:4], 1):
                    self.device_tree.insert("", "end", values=("PC", f"PC-{i}.{j}", f"eth0", str(ip), subnet['netmask'], subnet['first_ip']))

        self.adjust_column_widths(self.result_tree)
        self.adjust_column_widths(self.binary_tree)
        self.adjust_column_widths(self.device_tree)

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def show_usable_ips(self):
        try:
            ip_address = self.ip_entry.get()
            subnet_mask = int(self.mask_entry.get())
            num_subnets = int(self.subnets_entry.get())

            result = self.calculator.calculate_subnets(ip_address, subnet_mask, num_subnets)
            
            self.ip_list_text.delete(1.0, tk.END)
            for i, subnet in enumerate(result['subnets'], 1):
                network = ipaddress.IPv4Network(f"{subnet['network']}/{subnet['netmask']}", strict=False)
                usable_ips = list(network.hosts())
                
                self.ip_list_text.insert(tk.END, f"IPs utilizables para Subred {i} ({subnet['network']}/{subnet['netmask']}):\n")
                for ip in usable_ips:
                    self.ip_list_text.insert(tk.END, f"{ip}\n")
                self.ip_list_text.insert(tk.END, "\n")

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

    def show_guide(self):
        guide_text = """
        Guía de Subnetting y Uso del Programa:

        1. Comprender la Red Original:
           - Identifica la dirección IP de red y la máscara de subred.
           - Ejemplo: 192.168.1.0/24 (IP de red: 192.168.1.0, Máscara: 255.255.255.0)

        2. Determinar Requisitos:
           - Decide cuántas subredes necesitas.
           - Calcula cuántos hosts necesitas por subred.

        3. Calcular Nueva Máscara de Subred:
           - Toma prestados bits de la porción de host para crear subredes.
           - Ejemplo: Para 4 subredes, necesitas 2 bits, nueva máscara: /26

        4. Calcular Rango de Subredes:
           - Usa la nueva máscara para determinar las direcciones de red de cada subred.
           - Ejemplo: 192.168.1.0/26, 192.168.1.64/26, 192.168.1.128/26, 192.168.1.192/26

        5. Determinar Rango de Hosts:
           - Para cada subred, la primera IP utilizable es la dirección de red + 1.
           - La última IP utilizable es la dirección de broadcast - 1.

        Uso del Programa:
        1. Ingresa la dirección IP de red en el campo "Dirección IP".
        2. Ingresa la máscara de subred en notación CIDR en "Máscara de subred (CIDR)".
        3. Especifica el número de subredes deseadas en "Número de subredes".
        4. Haz clic en "Calcular" para obtener los resultados.

        Nomenclatura según Cisco:
        - Dirección de Red: Primera dirección de cada subred (no utilizable para hosts).
        - Primera IP Utilizable: Dirección de red + 1.
        - Última IP Utilizable: Dirección de broadcast - 1.
        - Dirección de Broadcast: Última dirección de cada subred (no utilizable para hosts).

        Nota: Según los lineamientos de Cisco, la dirección IP de red y la máscara deben ser compatibles. 
        El programa verificará esta compatibilidad automáticamente.
        """

        guide_window = tk.Toplevel(self.master)
        guide_window.title("Guía de Subnetting")
        guide_window.geometry("800x600")

        guide_text_widget = tk.Text(guide_window, wrap=tk.WORD, font=('Helvetica', 12))
        guide_text_widget.pack(expand=True, fill='both', padx=10, pady=10)
        guide_text_widget.insert(tk.END, guide_text)
        
        scrollbar = ttk.Scrollbar(guide_window, orient="vertical", command=guide_text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        guide_text_widget.configure(yscrollcommand=scrollbar.set)

    def validate_ip_and_mask(self):
        ip = self.ip_entry.get()
        mask = self.mask_entry.get()
        result = self.api_client.validate_ip_and_mask(ip, mask)
        if result['valid']:
            messagebox.showinfo("Validación", "La IP y la máscara son válidas.")
        else:
            messagebox.showerror("Error de validación", result['error'])

    def get_examples(self):
        try:
            examples = self.api_client.get_examples()
            logging.debug(f"Ejemplos recibidos: {examples}")
            if examples.get('examples'):
                example = random.choice(examples['examples'])
                self.ip_entry.delete(0, tk.END)
                self.ip_entry.insert(0, example['ip'])
                self.mask_entry.delete(0, tk.END)
                self.mask_entry.insert(0, example['mask'])
                self.subnets_entry.delete(0, tk.END)
                self.subnets_entry.insert(0, "4")  # Valor predeterminado para número de subredes
                messagebox.showinfo("Ejemplo", f"IP: {example['ip']}\nMáscara: {example['mask']}\nDescripción: {example['description']}")
            else:
                logging.error("No se recibieron ejemplos válidos")
                messagebox.showerror("Error", "No se pudieron obtener ejemplos.")
        except Exception as e:
            logging.exception("Error al obtener ejemplos")
            messagebox.showerror("Error", f"Ocurrió un error al obtener ejemplos: {str(e)}")

    def mostrar_mensaje(self, mensaje):
        messagebox.showinfo("Resultado de la verificación", mensaje)

    def adjust_column_widths(self, tree):
        for col in tree["columns"]:
            tree.column(col, width=tkinter.font.Font().measure(col) + 10)  # ancho basado en el encabezado
            # Ajusta el ancho de la columna al contenido más ancho
            for item in tree.get_children():
                cell_width = tkinter.font.Font().measure(tree.set(item, col)) + 10
                if tree.column(col, width=None) < cell_width:
                    tree.column(col, width=cell_width)