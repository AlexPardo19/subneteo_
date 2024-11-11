import tkinter as tk
from gui.subnet_calculator_gui import SubnetCalculatorGUI
import logging
import sys

def main():
    try:
        # Aumenta el límite de recursión
        sys.setrecursionlimit(10000)
        
        root = tk.Tk()
        app = SubnetCalculatorGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Se produjo un error: {e}")
        logging.exception("Error en la aplicación principal")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename='app_error.log', filemode='w',
                        format='%(asctime)s - %(levelname)s - %(message)s')
    main()
