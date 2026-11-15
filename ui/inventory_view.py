"""
inventory_view.py - Vista de Gestión de Catálogo e Inventario para StockMaster
Permite el alta, baja, modificación, búsqueda, filtrado y exportación de productos.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import database
from utils.helpers import format_currency, export_inventory_csv

class InventoryView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(padding=15)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # Header y Barra de búsqueda
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 10))

        title = ttk.Label(header_frame, text="📦 Catálogo y Control de Inventario", font=("Helvetica", 15, "bold"))
        title.pack(side="left")

        # Barra de filtros y búsqueda
        filter_frame = ttk.LabelFrame(self, text="🔍 Búsqueda y Filtros", padding=10)
        filter_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(filter_frame, text="Buscar:").pack(side="left", padx=(0, 5))
        self.var_search = tk.StringVar()
        self.var_search.trace_add("write", lambda *args: self.apply_filters())
        entry_search = ttk.Entry(filter_frame, textvariable=self.var_search, width=28)
        entry_search.pack(side="left", padx=(0, 15))

        ttk.Label(filter_frame, text="Categoría:").pack(side="left", padx=(0, 5))
        self.cb_category = ttk.Combobox(filter_frame, state="readonly", width=22)
        self.cb_category.pack(side="left", padx=(0, 15))
        self.cb_category.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        self.var_low_stock = tk.BooleanVar(value=False)
        chk_low = ttk.Checkbutton(filter_frame, text="⚠️ Solo stock bajo / crítico", variable=self.var_low_stock, command=self.apply_filters)
        chk_low.pack(side="left", padx=(0, 15))

        btn_clear = ttk.Button(filter_frame, text="Limpiar Filtros", command=self.reset_filters)
        btn_clear.pack(side="right")

        # Tabla de productos
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, pady=(0, 10))

        cols = ("id", "sku", "nombre", "categoria", "costo", "venta", "stock", "minimo", "ubicacion", "estado", "proveedor")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("sku", text="SKU")
        self.tree.heading("nombre", text="Nombre del Producto")
        self.tree.heading("categoria", text="Categoría")
        self.tree.heading("costo", text="Costo")
        self.tree.heading("venta", text="P. Venta")
        self.tree.heading("stock", text="Stock")
        self.tree.heading("minimo", text="Mín.")
        self.tree.heading("ubicacion", text="Ubicación")
        self.tree.heading("estado", text="Estado")
        self.tree.heading("proveedor", text="Proveedor")

        self.tree.column("id", width=45, anchor="center")
        self.tree.column("sku", width=85, anchor="center")
        self.tree.column("nombre", width=220, anchor="w")
        self.tree.column("categoria", width=130, anchor="w")
        self.tree.column("costo", width=75, anchor="e")
        self.tree.column("venta", width=75, anchor="e")
        self.tree.column("stock", width=65, anchor="center")
        self.tree.column("minimo", width=55, anchor="center")
        self.tree.column("ubicacion", width=120, anchor="w")
        self.tree.column("estado", width=100, anchor="center")
        self.tree.column("proveedor", width=160, anchor="w")

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        # Tags de color para el estado de stock
        self.tree.tag_configure("normal", foreground="#1E293B")
        self.tree.tag_configure("bajo", background="#FEF3C7", foreground="#92400E")
        self.tree.tag_configure("agotado", background="#FEE2E2", foreground="#991B1B")

        # Barra de botones de acción
        action_bar = ttk.Frame(self)
        action_bar.pack(fill="x", pady=5)

        btn_add = ttk.Button(action_bar, text="➕ Nuevo Producto", command=self.open_new_product_dialog)
        btn_add.pack(side="left", padx=4)

        btn_edit = ttk.Button(action_bar, text="✏️ Editar Producto", command=self.open_edit_product_dialog)
        btn_edit.pack(side="left", padx=4)

        btn_delete = ttk.Button(action_bar, text="🗑️ Eliminar", command=self.delete_selected_product)
        btn_delete.pack(side="left", padx=4)

        ttk.Separator(action_bar, orient="vertical").pack(side="left", fill="y", padx=10)

        btn_export = ttk.Button(action_bar, text="📥 Exportar a CSV (Excel)", command=self.export_csv)
        btn_export.pack(side="right", padx=4)

        self.lbl_count = ttk.Label(action_bar, text="0 productos mostrados", font=("Helvetica", 9, "italic"))
        self.lbl_count.pack(side="right", padx=15)

    def load_categories(self):
        """Carga las categorías en el combobox de filtro."""
        cats = database.get_categories()
        self.categories_map = {"TODAS": None}
        values = ["TODAS"]
        for c in cats:
            self.categories_map[c["nombre"]] = c["id"]
            values.append(c["nombre"])
        self.cb_category["values"] = values
        self.cb_category.current(0)

    def reset_filters(self):
        self.var_search.set("")
        self.cb_category.current(0)
        self.var_low_stock.set(False)
        self.apply_filters()

    def apply_filters(self):
        """Aplica los filtros de búsqueda y actualiza la tabla."""
        search = self.var_search.get()
        cat_name = self.cb_category.get()
        cat_id = self.categories_map.get(cat_name) if hasattr(self, "categories_map") else None
        only_low = self.var_low_stock.get()

        products = database.get_products(search_text=search, category_id=cat_id, only_low_stock=only_low)

        for item in self.tree.get_children():
            self.tree.delete(item)

        for p in products:
            stock = p["stock_actual"]
            min_stk = p["stock_minimo"]
            
            if stock == 0:
                estado = "AGOTADO"
                tag = "agotado"
            elif stock <= min_stk:
                estado = "STOCK BAJO"
                tag = "bajo"
            else:
                estado = "NORMAL"
                tag = "normal"

            self.tree.insert("", "end", values=(
                p["id"],
                p["sku"],
                p["nombre"],
                p["categoria_nombre"] or "Sin Asignar",
                format_currency(p["precio_compra"]),
                format_currency(p["precio_venta"]),
                stock,
                min_stk,
                p["ubicacion"] or "-",
                estado,
                p["proveedor_nombre"] or "Sin Asignar"
            ), tags=(tag,))

        self.lbl_count.config(text=f"{len(products)} producto(s) en catálogo")

    def refresh(self):
        self.load_categories()
        self.apply_filters()

    def _get_selected_product_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Por favor seleccione un producto de la lista.")
            return None
        return self.tree.item(sel[0])["values"][0]

    def open_new_product_dialog(self):
        ProductDialog(self, title="Registrar Nuevo Producto", on_save=self.refresh)

    def open_edit_product_dialog(self):
        pid = self._get_selected_product_id()
        if pid:
            prod_data = database.get_product_by_id(pid)
            if prod_data:
                ProductDialog(self, title="Editar Producto", product_data=prod_data, on_save=self.refresh)

    def delete_selected_product(self):
        pid = self._get_selected_product_id()
        if not pid:
            return

        prod = database.get_product_by_id(pid)
        if not prod:
            return

        confirm = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar el producto '{prod['nombre']}' (SKU: {prod['sku']})?\n\nEsta acción no se puede deshacer."
        )
        if confirm:
            ok, msg = database.delete_product(pid)
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.refresh()
                if hasattr(self.controller, "refresh_dashboard"):
                    self.controller.refresh_dashboard()
            else:
                messagebox.showerror("No se pudo eliminar", msg)

    def export_csv(self):
        """Exporta la lista completa de inventario a un archivo CSV."""
        products = database.get_products()
        if not products:
            messagebox.showwarning("Aviso", "No hay productos disponibles para exportar.")
            return

        initial_file = "Reporte_Inventario.csv"
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivos CSV (Excel)", "*.csv"), ("Todos los archivos", "*.*")],
            initialfile=initial_file
        )
        if path:
            success = export_inventory_csv(products, path)
            if success:
                messagebox.showinfo("Exportación Exitosa", f"El archivo se guardó correctamente en:\n{path}")
            else:
                messagebox.showerror("Error", "No se pudo generar el archivo CSV.")


class ProductDialog(tk.Toplevel):
    """Diálogo modal para crear o editar un producto."""
    def __init__(self, parent, title="Producto", product_data=None, on_save=None):
        super().__init__(parent)
        self.title(title)
        self.product_data = product_data
        self.on_save = on_save
        self.geometry("480x560")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        if product_data:
            self._fill_data(product_data)

    def _build_ui(self):
        pad_options = {"padx": 15, "pady": 6}

        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)

        # SKU
        ttk.Label(main_frame, text="Código SKU: *").grid(row=0, column=0, sticky="w", **pad_options)
        self.entry_sku = ttk.Entry(main_frame, width=28)
        self.entry_sku.grid(row=0, column=1, sticky="w", **pad_options)

        # Nombre
        ttk.Label(main_frame, text="Nombre del Producto: *").grid(row=1, column=0, sticky="w", **pad_options)
        self.entry_name = ttk.Entry(main_frame, width=28)
        self.entry_name.grid(row=1, column=1, sticky="w", **pad_options)

        # Categoría
        ttk.Label(main_frame, text="Categoría:").grid(row=2, column=0, sticky="w", **pad_options)
        self.cb_category = ttk.Combobox(main_frame, state="readonly", width=25)
        self.cb_category.grid(row=2, column=1, sticky="w", **pad_options)

        # Proveedor
        ttk.Label(main_frame, text="Proveedor:").grid(row=3, column=0, sticky="w", **pad_options)
        self.cb_supplier = ttk.Combobox(main_frame, state="readonly", width=25)
        self.cb_supplier.grid(row=3, column=1, sticky="w", **pad_options)

        # Cargar categorías y proveedores
        cats = database.get_categories()
        self.cat_map = {c["nombre"]: c["id"] for c in cats}
        self.cb_category["values"] = list(self.cat_map.keys())
        if self.cb_category["values"]:
            self.cb_category.current(0)

        provs = database.get_suppliers()
        self.prov_map = {p["nombre"]: p["id"] for p in provs}
        self.cb_supplier["values"] = list(self.prov_map.keys())
        if self.cb_supplier["values"]:
            self.cb_supplier.current(0)

        # Precios
        ttk.Label(main_frame, text="Precio de Compra (Costo $): *").grid(row=4, column=0, sticky="w", **pad_options)
        self.entry_cost = ttk.Entry(main_frame, width=28)
        self.entry_cost.grid(row=4, column=1, sticky="w", **pad_options)

        ttk.Label(main_frame, text="Precio de Venta ($): *").grid(row=5, column=0, sticky="w", **pad_options)
        self.entry_price = ttk.Entry(main_frame, width=28)
        self.entry_price.grid(row=5, column=1, sticky="w", **pad_options)

        # Stock Inicial (solo habilitado en nuevo producto)
        ttk.Label(main_frame, text="Stock Inicial: *").grid(row=6, column=0, sticky="w", **pad_options)
        self.entry_stock = ttk.Entry(main_frame, width=28)
        self.entry_stock.grid(row=6, column=1, sticky="w", **pad_options)
        if self.product_data:
            self.entry_stock.config(state="disabled")

        # Stock Mínimo
        ttk.Label(main_frame, text="Stock Mínimo (Punto reorden): *").grid(row=7, column=0, sticky="w", **pad_options)
        self.entry_min = ttk.Entry(main_frame, width=28)
        self.entry_min.insert(0, "5")
        self.entry_min.grid(row=7, column=1, sticky="w", **pad_options)

        # Ubicación en Bodega
        ttk.Label(main_frame, text="Ubicación en Almacén:").grid(row=8, column=0, sticky="w", **pad_options)
        self.entry_loc = ttk.Entry(main_frame, width=28)
        self.entry_loc.insert(0, "Pasillo 1 - Estante A")
        self.entry_loc.grid(row=8, column=1, sticky="w", **pad_options)

        # Botones de Acción
        btn_box = ttk.Frame(main_frame)
        btn_box.grid(row=9, column=0, columnspan=2, pady=(20, 0))

        btn_save = ttk.Button(btn_box, text="💾 Guardar Producto", command=self.save)
        btn_save.pack(side="left", padx=10)

        btn_cancel = ttk.Button(btn_box, text="Cancelar", command=self.destroy)
        btn_cancel.pack(side="left", padx=10)

    def _fill_data(self, data):
        self.entry_sku.insert(0, data.get("sku", ""))
        self.entry_name.insert(0, data.get("nombre", ""))
        
        # Categoría
        cat_name = data.get("categoria_nombre")
        if cat_name in self.cat_map:
            self.cb_category.set(cat_name)

        # Proveedor
        prov_name = data.get("proveedor_nombre")
        if prov_name in self.prov_map:
            self.cb_supplier.set(prov_name)

        self.entry_cost.insert(0, str(data.get("precio_compra", "")))
        self.entry_price.insert(0, str(data.get("precio_venta", "")))
        self.entry_min.delete(0, tk.END)
        self.entry_min.insert(0, str(data.get("stock_minimo", "5")))
        self.entry_loc.delete(0, tk.END)
        self.entry_loc.insert(0, data.get("ubicacion", ""))
        self.entry_stock.config(state="normal")
        self.entry_stock.insert(0, str(data.get("stock_actual", "0")))
        self.entry_stock.config(state="disabled")

    def save(self):
        sku = self.entry_sku.get().strip().upper()
        nombre = self.entry_name.get().strip()

        if not sku or not nombre:
            messagebox.showwarning("Campos Requeridos", "El SKU y el Nombre del producto son obligatorios.", parent=self)
            return

        try:
            costo = float(self.entry_cost.get().strip())
            precio = float(self.entry_price.get().strip())
            stock_min = int(self.entry_min.get().strip())
            if costo < 0 or precio < 0 or stock_min < 0:
                raise ValueError("Los valores numéricos no pueden ser negativos.")
        except ValueError:
            messagebox.showwarning("Valores Inválidos", "Por favor introduzca precios y stock mínimo válidos y no negativos.", parent=self)
            return

        cat_id = self.cat_map.get(self.cb_category.get())
        prov_id = self.prov_map.get(self.cb_supplier.get())
        ubicacion = self.entry_loc.get().strip()

        if self.product_data:
            # Edición
            pid = self.product_data["id"]
            ok, msg = database.update_product(pid, sku, nombre, cat_id, prov_id, costo, precio, stock_min, ubicacion)
        else:
            # Creación
            try:
                stock_ini = int(self.entry_stock.get().strip())
                if stock_ini < 0:
                    raise ValueError()
            except ValueError:
                messagebox.showwarning("Stock Inicial Inválido", "El stock inicial debe ser un número entero mayor o igual a 0.", parent=self)
                return

            ok, msg = database.create_product(sku, nombre, cat_id, prov_id, costo, precio, stock_ini, stock_min, ubicacion)

        if ok:
            messagebox.showinfo("Éxito", msg, parent=self)
            if self.on_save:
                self.on_save()
            self.destroy()
        else:
            messagebox.showerror("Error al guardar", msg, parent=self)
