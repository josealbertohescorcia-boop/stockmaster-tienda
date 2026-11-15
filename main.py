"""
main.py - Punto de Entrada Principal para StockMaster
Sistema de Gestión de Almacén e Inventario para Tienda

Para ejecutar el sistema:
    python main.py
"""

import sys
import os

# Asegurar que el directorio raíz del proyecto esté en el PYTHONPATH
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import database
from ui.main_window import MainWindow

def main():
    """Función de arranque principal."""
    print("=" * 60)
    print("Iniciando StockMaster - Sistema de Almacén para Tienda")
    print("=" * 60)

    # 1. Inicializar base de datos y migraciones/semillas
    print("[1/2] Inicializando base de datos SQLite y verificando tablas...")
    database.init_db()
    print("      -> Base de datos lista y conectada correctamente.")

    # 2. Inicializar interfaz gráfica de usuario
    print("[2/2] Cargando interfaz de usuario (Tkinter)...")
    app = MainWindow()
    print("      -> Sistema listo. Ventana principal abierta.")
    print("=" * 60)

    # Bucle de eventos principal
    app.mainloop()

if __name__ == "__main__":
    main()
