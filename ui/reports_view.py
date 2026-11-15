"""
reports_view.py - Vista de Reportes Financieros y Análisis de Inventario para StockMaster
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import database
from utils.helpers import format_currency, format_date, export_inventory_csv, export_movements_csv

class ReportsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(padding=15)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))

        ttk.Label(header, text="📈 Reportes Financieros y Análisis de Almacén", font=("Helvetica", 15, "bold")).pack(side="left")

        btn_refresh = ttk.Button(header, text="🔄 Actualizar Reportes", command=self.refresh)
        btn_refresh.pack(side="right")

        # -----------------------------
        # RESUMEN VALUACIÓN ECONÓMICA
        # -----------------------------
        fin_frame = ttk.LabelFrame(self, text="💰 Valuación Económica y Rentabilidad de Almacén", padding=15)
        fin_frame.pack(fill="x", pady=(0, 15))

        for i in range(4):
            fin_frame.columnconfigure(i, weight=1)

        self.lbl_costo_total = self._build_stat_box(fin_frame, 0, "Valor en Almacén (Costo)", "$0.00", "#1E40AF")
        self.lbl_venta_total = self._build_stat_box(fin_frame, 1, "Valor Proyectado (Venta)", "$0.00", "#065F46")
        self.lbl_ganancia_proy = self._build_stat_box(fin_frame, 2, "Margen Bruto Proyectado", "$0.00", "#9333EA")
        self.lbl_margen_pct = self._build_stat_box(fin_frame, 3, "Margen de Ganancia Promedio", "0.0%", "#B45309")

        # -----------------------------
        # HISTORIAL DE VENTAS Y SALIDAS
        # -----------------------------
        sales_frame = ttk.LabelFrame(self, text="🧾 Ventas y Despachos Recientes", padding=10)
        sales_frame.pack(fill="both", expand=True, pady=(0, 10))

        cols = ("folio", "fecha", "articulos", "subtotal", "iva", "total", "metodo")
        self.tree_sales = ttk.Treeview(sales_frame, columns=cols, show="headings", selectmode="browse")
        self.tree_sales.heading("folio", text="Folio")
        self.tree_sales.heading("fecha", text="Fecha de Venta")
        self.tree_sales.heading("articulos", text="Líneas")
        self.tree_sales.heading("subtotal", text="Subtotal")
        self.tree_sales.heading("iva", text="IVA (16%)")
        self.tree_sales.heading("total", text="Total Facturado")
        self.tree_sales.heading("metodo", text="Método de Pago")

        self.tree_sales.column("folio", width=160, anchor="center")
        self.tree_sales.column("fecha", width=140, anchor="center")
        self.tree_sales.column("articulos", width=70, anchor="center")
        self.tree_sales.column("subtotal", width=95, anchor="e")
        self.tree_sales.column("iva", width=85, anchor="e")
        self.tree_sales.column("total", width=110, anchor="e")
        self.tree_sales.column("metodo", width=130, anchor="center")

        scroll = ttk.Scrollbar(sales_frame, orient="vertical", command=self.tree_sales.yview)
        self.tree_sales.configure(yscrollcommand=scroll.set)
        self.tree_sales.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # -----------------------------
        # BOTONES DE EXPORTACIÓN
        # -----------------------------
        export_box = ttk.LabelFrame(self, text="📥 Centro de Exportación de Datos (Compatibles con Excel)", padding=10)
        export_box.pack(fill="x")

        ttk.Button(export_box, text="📊 Exportar Catálogo de Inventario (.CSV)", command=self.export_inventory).pack(side="left", padx=10)
        ttk.Button(export_box, text="🔄 Exportar Historial Kardex Completo (.CSV)", command=self.export_movements).pack(side="left", padx=10)
        ttk.Button(export_box, text="🧾 Exportar Historial de Ventas (.CSV)", command=self.export_sales).pack(side="left", padx=10)

    def _build_stat_box(self, parent, col, title, initial_val, color):
        box = tk.Frame(parent, bg="white", highlightbackground="#E2E8F0", highlightthickness=1, padx=12, pady=10)
        box.grid(row=0, column=col, padx=5, sticky="nsew")

        lbl_t = tk.Label(box, text=title, font=("Helvetica", 9, "bold"), fg="#64748B", bg="white", anchor="w")
        lbl_t.pack(fill="x")

        lbl_v = tk.Label(box, text=initial_val, font=("Helvetica", 15, "bold"), fg=color, bg="white", anchor="w", pady=2)
        lbl_v.pack(fill="x")
        return lbl_v

    def refresh(self):
        stats = database.get_dashboard_metrics()
        costo_total = stats.get("valor_almacen_costo", 0.0)
        venta_total = stats.get("valor_almacen_venta", 0.0)
        ganancia = max(0.0, venta_total - costo_total)
        margen = (ganancia / costo_total * 100) if costo_total > 0 else 0.0

        self.lbl_costo_total.config(text=format_currency(costo_total))
        self.lbl_venta_total.config(text=format_currency(venta_total))
        self.lbl_ganancia_proy.config(text=format_currency(ganancia))
        self.lbl_margen_pct.config(text=f"{margen:.1f}%")

        # Cargar ventas recientes
        for item in self.tree_sales.get_children():
            self.tree_sales.delete(item)

        sales = database.get_recent_sales(limit=100)
        for s in sales:
            self.tree_sales.insert("", "end", values=(
                s["folio"],
                format_date(s["fecha_venta"]),
                s["total_articulos"],
                format_currency(s["subtotal"]),
                format_currency(s["iva"]),
                format_currency(s["total"]),
                s["metodo_pago"]
            ))

    def export_inventory(self):
        prods = database.get_products()
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], initialfile="Inventario_Almacen.csv")
        if path:
            if export_inventory_csv(prods, path):
                messagebox.showinfo("Éxito", f"Catálogo exportado en:\n{path}")

    def export_movements(self):
        movs = database.get_movements(limit=2000)
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], initialfile="Kardex_Movimientos.csv")
        if path:
            if export_movements_csv(movs, path):
                messagebox.showinfo("Éxito", f"Kardex exportado en:\n{path}")

    def export_sales(self):
        sales = database.get_recent_sales(limit=2000)
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], initialfile="Historial_Ventas.csv")
        if path:
            try:
                with open(path, mode="w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Folio", "Fecha", "Líneas de Artículos", "Subtotal", "IVA", "Total", "Método de Pago"])
                    for s in sales:
                        writer.writerow([s["id"], s["folio"], s["fecha_venta"], s["total_articulos"], f"{s['subtotal']:.2f}", f"{s['iva']:.2f}", f"{s['total']:.2f}", s["metodo_pago"]])
                messagebox.showinfo("Éxito", f"Ventas exportadas en:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar: {e}")
