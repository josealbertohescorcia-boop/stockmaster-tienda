"""
main_window.py - Ventana Principal y Controlador de Navegación de StockMaster
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime

from ui.dashboard_view import DashboardView
from ui.inventory_view import InventoryView
from ui.movements_view import MovementsView
from ui.pos_view import POSView
from ui.suppliers_view import SuppliersView
from ui.reports_view import ReportsView

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("StockMaster v1.0 | Sistema de Gestión de Almacén e Inventario")
        self.geometry("1160x730")
        self.minsize(980, 620)

        # Centrar ventana en pantalla
        self._center_window(1160, 730)

        # Configurar estilos visuales TTK
        self._setup_styles()

        # Construir estructura de la interfaz
        self._build_header()
        self._build_body()
        self._build_statusbar()

        # Cargar vista inicial
        self.show_view("dashboard")

    def _center_window(self, width, height):
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _setup_styles(self):
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        # Configuración general
        self.style.configure(".", font=("Helvetica", 10), background="#F8FAFC")
        self.style.configure("TFrame", background="#F8FAFC")
        self.style.configure("TLabelframe", background="#F8FAFC")
        self.style.configure("TLabelframe.Label", font=("Helvetica", 10, "bold"), foreground="#1E293B", background="#F8FAFC")
        self.style.configure("TLabel", background="#F8FAFC", foreground="#1E293B")
        
        # Estilo de Botones
        self.style.configure("TButton", font=("Helvetica", 9, "bold"), padding=6)
        
        # Estilo de Tablas Treeview
        self.style.configure("Treeview", 
                             font=("Helvetica", 9), 
                             rowheight=26,
                             background="#FFFFFF", 
                             fieldbackground="#FFFFFF",
                             foreground="#1E293B")
        self.style.configure("Treeview.Heading", 
                             font=("Helvetica", 9, "bold"), 
                             background="#E2E8F0", 
                             foreground="#1E293B",
                             padding=5)
        self.style.map("Treeview", background=[("selected", "#2563EB")], foreground=[("selected", "#FFFFFF")])

    def _build_header(self):
        header = tk.Frame(self, bg="#1E3A8A", height=70, padx=20, pady=10)
        header.pack(fill="x", side="top")

        # Logotipo y Título
        info_frame = tk.Frame(header, bg="#1E3A8A")
        info_frame.pack(side="left", fill="y")

        lbl_app = tk.Label(info_frame, text="🏪 StockMaster", font=("Helvetica", 16, "bold"), fg="#FFFFFF", bg="#1E3A8A")
        lbl_app.pack(anchor="w")

        lbl_sub = tk.Label(info_frame, text="Sistema Integral de Almacén, Kardex y Punto de Salida para Tiendas", font=("Helvetica", 9), fg="#93C5FD", bg="#1E3A8A")
        lbl_sub.pack(anchor="w")

        # Badges de usuario y alertas
        right_meta = tk.Frame(header, bg="#1E3A8A")
        right_meta.pack(side="right", fill="y")

        self.btn_alert_badge = tk.Button(
            right_meta, text="⚠️ 0 Alertas de Stock", font=("Helvetica", 9, "bold"),
            bg="#DC2626", fg="white", activebackground="#B91C1C", activeforeground="white",
            relief="flat", padx=10, pady=4, cursor="hand2", command=self._on_alert_click
        )
        self.btn_alert_badge.pack(side="right", padx=(10, 0))

        lbl_user = tk.Label(right_meta, text="👤 Usuario: Administrador", font=("Helvetica", 9, "bold"), fg="#FFFFFF", bg="#1E3A8A")
        lbl_user.pack(side="right", padx=10)

    def _build_body(self):
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True)

        # -----------------------------
        # BARRA LATERAL (SIDEBAR DE NAVEGACIÓN)
        # -----------------------------
        self.sidebar = tk.Frame(body, bg="#0F172A", width=220, padx=10, pady=15)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        lbl_nav = tk.Label(self.sidebar, text="MÓDULOS DEL SISTEMA", font=("Helvetica", 8, "bold"), fg="#64748B", bg="#0F172A")
        lbl_nav.pack(anchor="w", pady=(0, 10), padx=5)

        self.nav_buttons = {}
        modules = [
            ("dashboard", "📊 Panel de Control", "dashboard"),
            ("inventario", "📦 Inventario de Tienda", "inventario"),
            ("movimientos", "🔄 Kardex / Movimientos", "movimientos"),
            ("pos", "🛒 Despacho / Punto Venta", "pos"),
            ("proveedores", "👥 Proveedores & Cat.", "proveedores"),
            ("reportes", "📈 Reportes Financieros", "reportes"),
        ]

        for code, label, key in modules:
            btn = tk.Button(
                self.sidebar, text=label, font=("Helvetica", 10),
                fg="#E2E8F0", bg="#1E293B", activebackground="#2563EB", activeforeground="#FFFFFF",
                anchor="w", relief="flat", padx=12, pady=10, cursor="hand2",
                command=lambda k=key: self.show_view(k)
            )
            btn.pack(fill="x", pady=3)
            self.nav_buttons[key] = btn

        # Separador y Botón Acerca de
        sep = tk.Frame(self.sidebar, bg="#334155", height=1)
        sep.pack(fill="x", pady=15)

        btn_about = tk.Button(
            self.sidebar, text="ℹ️ Información de Entrega", font=("Helvetica", 9),
            fg="#94A3B8", bg="#0F172A", activebackground="#334155", activeforeground="#FFFFFF",
            relief="flat", anchor="w", padx=12, pady=6, cursor="hand2",
            command=self._show_about_dialog
        )
        btn_about.pack(fill="x", side="bottom", pady=5)

        # -----------------------------
        # ÁREA DE CONTENIDO PRINCIPAL
        # -----------------------------
        self.content_area = ttk.Frame(body)
        self.content_area.pack(side="right", fill="both", expand=True)

        # Instanciar vistas
        self.views = {
            "dashboard": DashboardView(self.content_area, self),
            "inventario": InventoryView(self.content_area, self),
            "movimientos": MovementsView(self.content_area, self),
            "pos": POSView(self.content_area, self),
            "proveedores": SuppliersView(self.content_area, self),
            "reportes": ReportsView(self.content_area, self),
        }

    def _build_statusbar(self):
        self.statusbar = tk.Frame(self, bg="#E2E8F0", height=24, padx=15)
        self.statusbar.pack(fill="x", side="bottom")

        self.lbl_status_db = tk.Label(self.statusbar, text="🟢 Base de Datos: SQLite Local Conectada (data/inventario.db)", font=("Helvetica", 8), fg="#334155", bg="#E2E8F0")
        self.lbl_status_db.pack(side="left")

        self.lbl_status_time = tk.Label(self.statusbar, text=datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), font=("Helvetica", 8), fg="#64748B", bg="#E2E8F0")
        self.lbl_status_time.pack(side="right")

    def show_view(self, view_key, action=None):
        """Cambia dinámicamente la vista mostrada en el área central."""
        if view_key not in self.views:
            return

        # Ocultar todas las vistas
        for v in self.views.values():
            v.pack_forget()

        # Resaltar botón activo en la barra lateral
        for k, btn in self.nav_buttons.items():
            if k == view_key:
                btn.config(bg="#2563EB", fg="#FFFFFF", font=("Helvetica", 10, "bold"))
            else:
                btn.config(bg="#1E293B", fg="#E2E8F0", font=("Helvetica", 10))

        # Mostrar vista seleccionada
        view = self.views[view_key]
        view.pack(fill="both", expand=True)
        view.refresh()

        # Acciones contextuales opcionales
        if view_key == "inventario" and action == "nuevo":
            view.open_new_product_dialog()
        elif view_key == "movimientos" and action == "entrada":
            view.open_movement_dialog("ENTRADA")
        elif view_key == "movimientos" and action == "salida":
            view.open_movement_dialog("SALIDA")

    def update_alert_badge(self, alert_count):
        if alert_count > 0:
            self.btn_alert_badge.config(text=f"⚠️ {alert_count} Stock Crítico", bg="#DC2626")
        else:
            self.btn_alert_badge.config(text="✅ Inventario Óptimo", bg="#059669")

    def _on_alert_click(self):
        self.show_view("inventario")
        inv_view = self.views["inventario"]
        inv_view.var_low_stock.set(True)
        inv_view.apply_filters()

    def refresh_dashboard(self):
        self.views["dashboard"].refresh()

    def refresh_inventory(self):
        self.views["inventario"].refresh()

    def refresh_movements(self):
        self.views["movimientos"].refresh()

    def _show_about_dialog(self):
        msg = (
            "StockMaster - Sistema de Gestión de Almacén para Tienda\n\n"
            "Proyecto Final Académico de Ingeniería de Software / Programación\n\n"
            "• Arquitectura: Modelo-Vista-Controlador (MVC) modular\n"
            "• Lenguaje: Python 3 con interfaz Tkinter/TTk\n"
            "• Persistencia: Base de datos relacional SQLite3 con integridad referencial\n"
            "• Seguridad: Sin claves privadas, API keys ni credenciales en código\n"
            "• Declaración de IA: Asistencia de Antigravity (Gemini) para diseño arquitectónico y documentación.\n\n"
            "Todos los derechos reservados © 2026"
        )
        messagebox.showinfo("Acerca del Proyecto", msg, parent=self)
