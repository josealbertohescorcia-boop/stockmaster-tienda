"""
dashboard_view.py - Vista de Panel de Control y Métricas para StockMaster
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
from utils.helpers import format_currency

class DashboardView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(padding=20)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # Título del Dashboard
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 15))

        title_lbl = ttk.Label(header_frame, text="📊 Panel de Control y Resumen Ejecutivo", font=("Helvetica", 16, "bold"))
        title_lbl.pack(side="left")

        btn_refresh = ttk.Button(header_frame, text="🔄 Actualizar Datos", command=self.refresh)
        btn_refresh.pack(side="right")

        # -----------------------------
        # TARJETAS KPI (INDICADORES)
        # -----------------------------
        cards_frame = ttk.Frame(self)
        cards_frame.pack(fill="x", pady=(0, 20))

        # Configurar 4 columnas proporcionales
        for i in range(4):
            cards_frame.columnconfigure(i, weight=1, uniform="card")

        self.card_prods = self._create_kpi_card(cards_frame, 0, "📦 Total Productos", "0", "#2563EB", "Unidades en catálogo")
        self.card_val = self._create_kpi_card(cards_frame, 1, "💰 Valor Almacén (Costo)", "$0.00", "#059669", "Inversión en existencias")
        self.card_alerts = self._create_kpi_card(cards_frame, 2, "⚠️ Alertas Stock Bajo", "0", "#DC2626", "Requieren reabastecimiento")
        self.card_sales = self._create_kpi_card(cards_frame, 3, "💵 Ventas del Día", "$0.00", "#7C3AED", "Total facturado hoy")

        # -----------------------------
        # ACCIONES RÁPIDAS
        # -----------------------------
        quick_actions_frame = ttk.LabelFrame(self, text="⚡ Acciones Rápidas de Almacén", padding=12)
        quick_actions_frame.pack(fill="x", pady=(0, 20))

        btn_new_prod = ttk.Button(quick_actions_frame, text="➕ Nuevo Producto", command=lambda: self.controller.show_view("inventario", action="nuevo"))
        btn_new_prod.pack(side="left", padx=6)

        btn_in = ttk.Button(quick_actions_frame, text="📥 Registrar Entrada de Mercancía", command=lambda: self.controller.show_view("movimientos", action="entrada"))
        btn_in.pack(side="left", padx=6)

        btn_out = ttk.Button(quick_actions_frame, text="📤 Registrar Salida / Merma", command=lambda: self.controller.show_view("movimientos", action="salida"))
        btn_out.pack(side="left", padx=6)

        btn_pos = ttk.Button(quick_actions_frame, text="🛒 Despacho / Punto de Venta", command=lambda: self.controller.show_view("pos"))
        btn_pos.pack(side="left", padx=6)

        # -----------------------------
        # TABLA DE PRODUCTOS EN ALERTA CRÍTICA
        # -----------------------------
        alert_frame = ttk.LabelFrame(self, text="🚨 Productos con Existencia Crítica o Stock Bajo (Reorden Necesario)", padding=10)
        alert_frame.pack(fill="both", expand=True)

        cols = ("sku", "nombre", "categoria", "stock_actual", "stock_minimo", "ubicacion", "proveedor")
        self.tree_alerts = ttk.Treeview(alert_frame, columns=cols, show="headings", height=8, selectmode="browse")
        
        self.tree_alerts.heading("sku", text="SKU")
        self.tree_alerts.heading("nombre", text="Nombre del Producto")
        self.tree_alerts.heading("categoria", text="Categoría")
        self.tree_alerts.heading("stock_actual", text="Stock Actual")
        self.tree_alerts.heading("stock_minimo", text="Stock Mínimo")
        self.tree_alerts.heading("ubicacion", text="Ubicación")
        self.tree_alerts.heading("proveedor", text="Proveedor Sugerido")

        self.tree_alerts.column("sku", width=90, anchor="center")
        self.tree_alerts.column("nombre", width=250, anchor="w")
        self.tree_alerts.column("categoria", width=140, anchor="w")
        self.tree_alerts.column("stock_actual", width=90, anchor="center")
        self.tree_alerts.column("stock_minimo", width=90, anchor="center")
        self.tree_alerts.column("ubicacion", width=130, anchor="w")
        self.tree_alerts.column("proveedor", width=180, anchor="w")

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(alert_frame, orient="vertical", command=self.tree_alerts.yview)
        self.tree_alerts.configure(yscrollcommand=scrollbar.set)
        
        self.tree_alerts.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Estilo visual de filas críticas
        self.tree_alerts.tag_configure("critico", background="#FEE2E2", foreground="#991B1B")
        self.tree_alerts.tag_configure("agotado", background="#FCA5A5", foreground="#7F1D1D")

    def _create_kpi_card(self, parent, col, title, initial_val, color, subtitle):
        """Crea una tarjeta KPI estilizada con relieve suave y colores de acento."""
        card = tk.Frame(parent, bg="white", highlightbackground="#E2E8F0", highlightthickness=1, padx=14, pady=12)
        card.grid(row=0, column=col, padx=6, sticky="nsew")

        lbl_title = tk.Label(card, text=title, font=("Helvetica", 10, "bold"), fg="#475569", bg="white", anchor="w")
        lbl_title.pack(fill="x")

        lbl_val = tk.Label(card, text=initial_val, font=("Helvetica", 18, "bold"), fg=color, bg="white", anchor="w", pady=4)
        lbl_val.pack(fill="x")

        lbl_sub = tk.Label(card, text=subtitle, font=("Helvetica", 8), fg="#94A3B8", bg="white", anchor="w")
        lbl_sub.pack(fill="x")

        return lbl_val

    def refresh(self):
        """Recalcula las estadísticas de la base de datos y refresca la tabla de alertas."""
        try:
            stats = database.get_dashboard_metrics()
            self.card_prods.config(text=str(stats.get("total_productos", 0)))
            self.card_val.config(text=format_currency(stats.get("valor_almacen_costo", 0.0)))
            self.card_alerts.config(text=str(stats.get("alertas_stock_bajo", 0)))
            self.card_sales.config(text=format_currency(stats.get("ingresos_hoy", 0.0)))

            # Cargar alertas
            for item in self.tree_alerts.get_children():
                self.tree_alerts.delete(item)

            alerts = database.get_low_stock_alerts()
            for a in alerts:
                tag = "agotado" if a["stock_actual"] == 0 else "critico"
                self.tree_alerts.insert("", "end", values=(
                    a["sku"],
                    a["nombre"],
                    a["categoria"] or "General",
                    f"{a['stock_actual']} uds.",
                    f"{a['stock_minimo']} uds.",
                    a["ubicacion"] or "-",
                    a["proveedor"] or "No asignado"
                ), tags=(tag,))

            # Notificar al controlador si existen alertas activas
            if hasattr(self.controller, "update_alert_badge"):
                self.controller.update_alert_badge(len(alerts))

        except Exception as e:
            messagebox.showerror("Error al cargar Dashboard", f"Ocurrió un error: {e}")
