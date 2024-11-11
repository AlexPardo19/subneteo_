import tkinter as tk
from tkinter import ttk

class SubnetVisualizer:
    def __init__(self, root):
        self.frame = ttk.Frame(root)
        self.frame.grid(sticky="nsew")
        
        self.canvas = tk.Canvas(self.frame, width=800, height=200, bg='white')
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        self.scrollbar = ttk.Scrollbar(self.frame, orient="horizontal", command=self.canvas.xview)
        self.scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.canvas.configure(xscrollcommand=self.scrollbar.set)
        
        # Configurar el grid para que se expanda correctamente
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

    def draw_subnets(self, subnets):
        self.canvas.delete("all")
        num_subnets = len(subnets)
        width = 200  # Ancho fijo para cada subred
        total_width = width * num_subnets
        self.canvas.configure(scrollregion=(0, 0, total_width, 200))
        colors = ['#FFB3BA', '#BAFFC9', '#BAE1FF', '#FFFFBA']  # Colores pastel

        for i, subnet in enumerate(subnets):
            x1 = i * width
            x2 = (i + 1) * width
            color = colors[i % len(colors)]
            self.canvas.create_rectangle(x1, 20, x2, 180, fill=color, outline='')
            self.canvas.create_text((x1 + x2) / 2, 40, text=f"Subred {i+1}", font=("Arial", 10, "bold"))
            self.canvas.create_text((x1 + x2) / 2, 70, text=str(subnet['network']), font=("Arial", 9))
            self.canvas.create_text((x1 + x2) / 2, 100, text=f"Primera IP: {subnet['first_ip']}", font=("Arial", 8))
            self.canvas.create_text((x1 + x2) / 2, 120, text=f"Última IP: {subnet['last_ip']}", font=("Arial", 8))
            self.canvas.create_text((x1 + x2) / 2, 140, text=f"Broadcast: {subnet['broadcast']}", font=("Arial", 8))
