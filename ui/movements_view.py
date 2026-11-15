"""
movements_view.py - Vista de Control de Movimientos y Kardex de Almacén para StockMaster
Permite registrar entradas por compras/reposición, salidas por merma/despacho,
ajustes de inventario físico y consultar el historial completo.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
from utils.helpers import format_currency, format_date, export_movements_csv

class MovementsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(padding=15)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 10))

        title = ttk.Label(header_frame, text="🔄 Movimientos de Almacén y Kardex", font=("Helvetica", 15, "bold"))
        title.pack(side="left")

        # Barra de Filtros
        filter_frame = ttk.LabelFrame(self, text="🔍 Filtrar Historial", padding=10)
        filter_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(filter_frame, text="Tipo de Movimiento:").pack(side="left", padx=(0, 5))
        self.cb_filter_type = ttk.Combobox(filter_frame, state="readonly", values=["TODOS", "ENTRADA", "SALIDA", "AJUSTE"], width=15)
        self.cb_filter_type.pack(side="left", padx=(0, 15))
        self.cb_filter_type.current(0)
        self.cb_filter_type.bind("<<ComboboxSelected>>", lambda e: self.load_movements())

        btn_refresh = ttk.Button(filter_frame, text="🔄 Actualizar", command=self.load_movements)
        btn_refresh.pack(side="left")

        btn_export = ttk.Button(filter_frame, text="📄 Exportar Kardex a CSV", command=self.export_csv)
        btn_export.pack(side="right")

        # Tabla de Movimientos
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, pady=(0, 10))

        cols = ("id", "fecha", "tipo", "sku", "producto", "cantidad", "costo", "motivo", "usuario")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        self.tree.heading("id", text="Folio Mov.")
        self.tree.heading("fecha", text="Fecha y Hora")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("sku", text="SKU")
        self.tree.heading("producto", text="Producto")
        self.tree.heading("cantidad", text="Cantidad")
        self.tree.heading("costo", text="Costo Unit.")
        self.tree.heading("motivo", text="Motivo / Detalle")
        self.tree.heading("usuario", text="Usuario")

        self.tree.column("id", width=75, anchor="center")
        self.tree.column("fecha", width=140, anchor="center")
        self.tree.column("tipo", width=95, anchor="center")
        self.tree.column("sku", width=85, anchor="center")
        self.tree.column("producto", width=220, anchor="w")
        self.tree.column("cantidad", width=80, anchor="center")
        self.tree.column("costo", width=90, anchor="e")
        self.tree.column("motivo", width=230, anchor="w")
        self.tree.column("usuario", width=110, anchor="center")

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        # Tags de color para tipos de movimiento
        self.tree.tag_configure("ENTRADA", foreground="#047857", background="#D1FAE5")
        self.tree.tag_configure("SALIDA", foreground="#B91C1C", background="#FEE2E2")
        self.tree.tag_configure("AJUSTE", foreground="#1D4ED8", background="#DBEAFE")

        # Barra de Operaciones Rápidas
        actions_bar = ttk.LabelFrame(self, text="⚡ Operaciones Directas de Entrada / Salida", padding=10)
        actions_bar.pack(fill="x", pady=5)

        btn_in = ttk.Button(actions_bar, text="📥 Registrar Entrada (Reabastecimiento)", command=lambda: self.open_movement_dialog("ENTRADA"))
        btn_in.pack(side="left", padx=8)

        btn_out = ttk.Button(actions_bar, text="📤 Registrar Salida (Merma / Devolución)", command=lambda: self.open_movement_dialog("SALIDA"))
        btn_out.pack(side="left", padx=8)

        btn_adj = ttk.Button(actions_bar, text="⚖️ Registrar Conteo Físico / Ajuste", command=lambda: self.open_movement_dialog("AJUSTE"))
        btn_adj.pack(side="left", padx=8)

    def load_movements(self):
        tipo = self.cb_filter_type.get()
        movements = database.get_movements(limit=300, tipo=tipo)

        for item in self.tree.get_children():
            self.tree.delete(item)

        for m in movements:
            self.tree.insert("", "end", values=(
                f"MOV-{m['id']:04d}",
                format_date(m["fecha_movimiento"]),
                m["tipo"],
                m["sku"],
                m["producto_nombre"],
                f"{m['cantidad']} uds.",
                format_currency(m["costo_unitario"]),
                m["motivo"] or "-",
                m["usuario"] or "Admin"
            ), tags=(m["tipo"],))

    def refresh(self):
        self.load_movements()

    def open_movement_dialog(self, tipo: str):
        MovementDialog(self, tipo=tipo, on_success=self._on_movement_recorded)

    def _on_movement_recorded(self):
        self.refresh()
        if hasattr(self.controller, "refresh_dashboard"):
            self.controller.refresh_dashboard()
        if hasattr(self.controller, "refresh_inventory"):
            self.controller.refresh_inventory()

    def export_csv(self):
        tipo = self.cb_filter_type.get()
        movements = database.get_movements(limit=1000, tipo=tipo)
        if not movements:
            messagebox.showwarning("Sin Datos", "No hay movimientos registrados para exportar.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivos CSV (Excel)", "*.csv"), ("Todos los archivos", "*.*")],
            initialfile=f"Kardex_Movimientos_{tipo}.csv"
        )
        if path:
            ok = export_movements_csv(movements, path)
            if ok:
                messagebox.showinfo("Exportación Exitosa", f"Archivo exportado correctamente en:\n{path}")
            else:
                messagebox.showerror("Error", "No se pudo exportar el archivo CSV.")


class MovementDialog(tk.Toplevel):
    """Diálogo modal para registrar una Entrada, Salida o Ajuste."""
    def __init__(self, parent, tipo="ENTRADA", on_success=None):
        super().__init__(parent)
        self.tipo = tipo
        self.on_success = on_success
        titles = {
            "ENTRADA": "📥 Registrar Entrada de Mercancía (Compra / Reposición)",
            "SALIDA": "📤 Registrar Salida de Mercancía (Merma / Ajuste / Pérdida)",
            "AJUSTE": "⚖️ Ajuste por Conteo Físico de Inventario"
        }
        self.title(titles.get(tipo, "Movimiento"))
        self.geometry("520x460")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        main = ttk.Frame(self, padding=20)
        main.pack(fill="both", expand=True)

        pad = {"padx": 10, "pady": 8}

        # Selección de Producto
        ttk.Label(main, text="Seleccionar Producto: *").grid(row=0, column=0, sticky="w", **pad)
        self.cb_products = ttk.Combobox(main, state="readonly", width=36)
        self.cb_products.grid(row=0, column=1, sticky="w", **pad)
        self.cb_products.bind("<<ComboboxSelected>>", self._on_product_selected)

        # Cargar productos
        self.products = database.get_products()
        self.prod_map = {}
        values = []
        for p in self.products:
            label = f"[{p['sku']}] {p['nombre']} (Stock actual: {p['stock_actual']})"
            values.append(label)
            self.prod_map[label] = p
        self.cb_products["values"] = values

        # Detalle informativo del producto seleccionado
        self.lbl_info = ttk.Label(main, text="Seleccione un producto para ver existencias.", font=("Helvetica", 9, "italic"), foreground="#475569")
        self.lbl_info.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 10))

        # Cantidad
        qty_label = "Cantidad a ingresar: *" if self.tipo == "ENTRADA" else ("Cantidad a egresar: *" if self.tipo == "SALIDA" else "Conteo Físico Real: *")
        ttk.Label(main, text=qty_label).grid(row=2, column=0, sticky="w", **pad)
        self.entry_qty = ttk.Entry(main, width=20)
        self.entry_qty.grid(row=2, column=1, sticky="w", **pad)

        # Costo unitario (principalmente relevante para entradas)
        ttk.Label(main, text="Costo Unitario ($):").grid(row=3, column=0, sticky="w", **pad)
        self.entry_cost = ttk.Entry(main, width=20)
        self.entry_cost.grid(row=3, column=1, sticky="w", **pad)

        # Motivo
        ttk.Label(main, text="Motivo o Justificación: *").grid(row=4, column=0, sticky="w", **pad)
        self.cb_reason = ttk.Combobox(main, width=33)
        self.cb_reason.grid(row=4, column=1, sticky="w", **pad)

        reasons = {
            "ENTRADA": ["Compra de reposición a proveedor", "Llegada de pedido programado", "Devolución de cliente en buen estado", "Corrección de faltante"],
            "SALIDA": ["Producto caducado / vencido", "Mercancía dañada / merma", "Uso interno de tienda", "Devolución a proveedor", "Muestra promocional"],
            "AJUSTE": ["Ajuste por inventario físico mensual", "Corrección por descuadre", "Conteo cíclico auditado"]
        }
        self.cb_reason["values"] = reasons.get(self.tipo, ["Ajuste general"])
        if self.cb_reason["values"]:
            self.cb_reason.current(0)

        # Usuario Responsable
        ttk.Label(main, text="Usuario Responsable:").grid(row=5, column=0, sticky="w", **pad)
        self.entry_user = ttk.Entry(main, width=20)
        self.entry_user.insert(0, "Administrador Almacén")
        self.entry_user.grid(row=5, column=1, sticky="w", **pad)

        # Botones
        btn_box = ttk.Frame(main)
        btn_box.grid(row=6, column=0, columnspan=2, pady=(25, 0))

        btn_confirm = ttk.Button(btn_box, text=f"Confirmar {self.tipo.title()}", command=self.save)
        btn_confirm.pack(side="left", padx=10)

        btn_cancel = ttk.Button(btn_box, text="Cancelar", command=self.destroy)
        btn_cancel.pack(side="left", padx=10)

        if values:
            self.cb_products.current(0)
            self._on_product_selected(None)

    def _on_product_selected(self, event):
        val = self.cb_products.get()
        p = self.prod_map.get(val)
        if p:
            self.lbl_info.config(text=f"Existencias: {p['stock_actual']} uds. | Costo ref: {format_currency(p['precio_compra'])} | Ubicación: {p['ubicacion'] or 'Sin especificar'}")
            self.entry_cost.delete(0, tk.END)
            self.entry_cost.insert(0, str(p["precio_compra"]))

    def save(self):
        val = self.cb_products.get()
        p = self.prod_map.get(val)
        if not p:
            messagebox.showwarning("Atención", "Debe seleccionar un producto.", parent=self)
            return

        try:
            qty = int(self.entry_qty.get().strip())
            if qty <= 0 and self.tipo != "AJUSTE":
                raise ValueError("La cantidad debe ser mayor a 0.")
            if qty < 0 and self.tipo == "AJUSTE":
                raise ValueError("El conteo físico no puede ser negativo.")
        except ValueError:
            messagebox.showwarning("Cantidad Inválida", "Por favor introduzca un número entero válido.", parent=self)
            return

        try:
            costo = float(self.entry_cost.get().strip())
        except ValueError:
            costo = p["precio_compra"]

        motivo = self.cb_reason.get().strip()
        if not motivo:
            motivo = f"Movimiento tipo {self.tipo}"

        usuario = self.entry_user.get().strip() or "Administrador"

        # Validaciones de regla de negocio
        if self.tipo == "SALIDA" and qty > p["stock_actual"]:
            messagebox.showerror(
                "Stock Insuficiente",
                f"No puede retirar {qty} unidades porque solo existen {p['stock_actual']} unidades en almacén.",
                parent=self
            )
            return

        ok, msg = database.register_movement(
            product_id=p["id"],
            tipo=self.tipo,
            cantidad=qty,
            costo_unitario=costo,
            motivo=motivo,
            usuario=usuario
        )

        if ok:
            messagebox.showinfo("Operación Exitosa", msg, parent=self)
            if self.on_success:
                self.on_success()
            self.destroy()
        else:
            messagebox.showerror("Error al registrar", msg, parent=self)
