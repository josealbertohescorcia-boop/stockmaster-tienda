"""
pos_view.py - Módulo de Punto de Venta y Despacho Rápido para StockMaster
Permite realizar ventas directas en mostrador, calcular totales e impuestos,
descontar inventario en tiempo real y emitir tickets de comprobante.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
from utils.helpers import format_currency, generate_receipt_text

class POSView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.cart = []  # Lista de items: [{id, sku, nombre, precio_compra, precio_venta, cantidad, stock_disponible}]
        self.configure(padding=15)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # Título
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))

        ttk.Label(header, text="🛒 Despacho Rápido y Punto de Venta", font=("Helvetica", 15, "bold")).pack(side="left")

        # Contenedor principal dividido en dos columnas (Izquierda: Catálogo, Derecha: Carrito)
        content_pane = ttk.PanedWindow(self, orient="horizontal")
        content_pane.pack(fill="both", expand=True)

        # -------------------------------------
        # PANEL IZQUIERDO: CATÁLOGO DE PRODUCTOS
        # -------------------------------------
        left_frame = ttk.LabelFrame(content_pane, text="📦 Catálogo de Productos Disponibles", padding=10)
        content_pane.add(left_frame, weight=3)

        # Buscador
        search_box = ttk.Frame(left_frame)
        search_box.pack(fill="x", pady=(0, 10))

        ttk.Label(search_box, text="Buscar:").pack(side="left", padx=(0, 5))
        self.var_search = tk.StringVar()
        self.var_search.trace_add("write", lambda *a: self.search_catalog())
        entry_search = ttk.Entry(search_box, textvariable=self.var_search)
        entry_search.pack(side="left", fill="x", expand=True, padx=(0, 5))

        btn_clear = ttk.Button(search_box, text="X", width=3, command=lambda: self.var_search.set(""))
        btn_clear.pack(side="right")

        # Tabla del catálogo
        cat_cols = ("sku", "nombre", "precio", "stock")
        self.tree_cat = ttk.Treeview(left_frame, columns=cat_cols, show="headings", selectmode="browse")
        self.tree_cat.heading("sku", text="SKU")
        self.tree_cat.heading("nombre", text="Producto")
        self.tree_cat.heading("precio", text="Precio")
        self.tree_cat.heading("stock", text="Stock")

        self.tree_cat.column("sku", width=70, anchor="center")
        self.tree_cat.column("nombre", width=180, anchor="w")
        self.tree_cat.column("precio", width=70, anchor="e")
        self.tree_cat.column("stock", width=60, anchor="center")

        scroll_cat = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree_cat.yview)
        self.tree_cat.configure(yscrollcommand=scroll_cat.set)
        self.tree_cat.pack(side="left", fill="both", expand=True)
        scroll_cat.pack(side="right", fill="y")

        # Control de Agregar al Carrito
        add_box = ttk.Frame(left_frame, padding=(0, 10, 0, 0))
        add_box.pack(fill="x")

        ttk.Label(add_box, text="Cantidad:").pack(side="left", padx=(0, 5))
        self.spin_qty = ttk.Spinbox(add_box, from_=1, to=999, width=5)
        self.spin_qty.set(1)
        self.spin_qty.pack(side="left", padx=(0, 10))

        btn_add = ttk.Button(add_box, text="➕ Agregar al Carrito", command=self.add_to_cart)
        btn_add.pack(side="left", fill="x", expand=True)

        # -------------------------------------
        # PANEL DERECHO: DETALLE DEL DESPACHO / TICKET
        # -------------------------------------
        right_frame = ttk.LabelFrame(content_pane, text="🛍️ Carrito de Despacho", padding=10)
        content_pane.add(right_frame, weight=3)

        # Tabla del carrito
        cart_cols = ("sku", "nombre", "cant", "precio", "total")
        self.tree_cart = ttk.Treeview(right_frame, columns=cart_cols, show="headings", selectmode="browse")
        self.tree_cart.heading("sku", text="SKU")
        self.tree_cart.heading("nombre", text="Producto")
        self.tree_cart.heading("cant", text="Cant.")
        self.tree_cart.heading("precio", text="P. Unit.")
        self.tree_cart.heading("total", text="Total")

        self.tree_cart.column("sku", width=65, anchor="center")
        self.tree_cart.column("nombre", width=160, anchor="w")
        self.tree_cart.column("cant", width=50, anchor="center")
        self.tree_cart.column("precio", width=70, anchor="e")
        self.tree_cart.column("total", width=75, anchor="e")

        scroll_cart = ttk.Scrollbar(right_frame, orient="vertical", command=self.tree_cart.yview)
        self.tree_cart.configure(yscrollcommand=scroll_cart.set)
        self.tree_cart.pack(side="top", fill="both", expand=True)
        scroll_cart.pack(side="right", fill="y")

        # Botones de eliminar del carrito
        btn_cart_box = ttk.Frame(right_frame, padding=(0, 5))
        btn_cart_box.pack(fill="x")

        btn_remove = ttk.Button(btn_cart_box, text="➖ Quitar Seleccionado", command=self.remove_from_cart)
        btn_remove.pack(side="left", padx=(0, 5))

        btn_clear_cart = ttk.Button(btn_cart_box, text="🗑️ Vaciar Carrito", command=self.clear_cart)
        btn_clear_cart.pack(side="left")

        # Totales y Métodos de Pago
        totals_frame = tk.Frame(right_frame, bg="#F1F5F9", padx=12, pady=10)
        totals_frame.pack(fill="x", pady=10)

        # Fila Subtotal
        f_sub = tk.Frame(totals_frame, bg="#F1F5F9")
        f_sub.pack(fill="x", pady=2)
        tk.Label(f_sub, text="Subtotal:", font=("Helvetica", 10), bg="#F1F5F9", fg="#475569").pack(side="left")
        self.lbl_subtotal = tk.Label(f_sub, text="$0.00", font=("Helvetica", 10, "bold"), bg="#F1F5F9", fg="#1E293B")
        self.lbl_subtotal.pack(side="right")

        # Fila IVA
        f_iva = tk.Frame(totals_frame, bg="#F1F5F9")
        f_iva.pack(fill="x", pady=2)
        tk.Label(f_iva, text="IVA (16%):", font=("Helvetica", 10), bg="#F1F5F9", fg="#475569").pack(side="left")
        self.lbl_iva = tk.Label(f_iva, text="$0.00", font=("Helvetica", 10, "bold"), bg="#F1F5F9", fg="#1E293B")
        self.lbl_iva.pack(side="right")

        # Fila Total
        f_tot = tk.Frame(totals_frame, bg="#F1F5F9")
        f_tot.pack(fill="x", pady=(5, 0))
        tk.Label(f_tot, text="TOTAL A COBRAR:", font=("Helvetica", 12, "bold"), bg="#F1F5F9", fg="#0F172A").pack(side="left")
        self.lbl_total = tk.Label(f_tot, text="$0.00", font=("Helvetica", 14, "bold"), bg="#F1F5F9", fg="#16A34A")
        self.lbl_total.pack(side="right")

        # Método de Pago
        pay_box = ttk.Frame(right_frame, padding=(0, 5))
        pay_box.pack(fill="x")

        ttk.Label(pay_box, text="Método de Pago:").pack(side="left", padx=(0, 5))
        self.cb_payment = ttk.Combobox(pay_box, state="readonly", values=["Efectivo", "Tarjeta de Débito", "Tarjeta de Crédito", "Transferencia Móvil"], width=20)
        self.cb_payment.current(0)
        self.cb_payment.pack(side="left", fill="x", expand=True)

        # Botón Cobrar
        btn_checkout = tk.Button(
            right_frame, text="✅ PROCESAR DESPACHO / VENTA",
            font=("Helvetica", 11, "bold"), bg="#2563EB", fg="white",
            activebackground="#1D4ED8", activeforeground="white",
            relief="flat", pady=8, cursor="hand2", command=self.process_checkout
        )
        btn_checkout.pack(fill="x", pady=(8, 0))

    def refresh(self):
        self.search_catalog()

    def search_catalog(self):
        query = self.var_search.get()
        prods = database.get_products(search_text=query)

        for item in self.tree_cat.get_children():
            self.tree_cat.delete(item)

        self.catalog_map = {}
        for p in prods:
            item_id = self.tree_cat.insert("", "end", values=(
                p["sku"],
                p["nombre"],
                format_currency(p["precio_venta"]),
                f"{p['stock_actual']} uds."
            ))
            self.catalog_map[item_id] = p

    def add_to_cart(self):
        sel = self.tree_cat.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un producto del catálogo para agregar.", parent=self)
            return

        prod = self.catalog_map.get(sel[0])
        if not prod:
            return

        try:
            qty = int(self.spin_qty.get().strip())
            if qty <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Cantidad Inválida", "La cantidad debe ser mayor a 0.", parent=self)
            return

        # Verificar si ya está en el carrito
        existing = next((item for item in self.cart if item["id"] == prod["id"]), None)
        total_requested = qty + (existing["cantidad"] if existing else 0)

        if total_requested > prod["stock_actual"]:
            messagebox.showerror(
                "Stock Insuficiente",
                f"No hay suficiente existencia de '{prod['nombre']}'.\nDisponible: {prod['stock_actual']}, solicitado en total: {total_requested}.",
                parent=self
            )
            return

        if existing:
            existing["cantidad"] = total_requested
        else:
            self.cart.append({
                "id": prod["id"],
                "sku": prod["sku"],
                "nombre": prod["nombre"],
                "precio_compra": prod["precio_compra"],
                "precio_venta": prod["precio_venta"],
                "cantidad": qty
            })

        self.spin_qty.set(1)
        self.update_cart_display()

    def remove_from_cart(self):
        sel = self.tree_cart.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un artículo del carrito para quitarlo.", parent=self)
            return
        idx = self.tree_cart.index(sel[0])
        if 0 <= idx < len(self.cart):
            del self.cart[idx]
            self.update_cart_display()

    def clear_cart(self):
        if self.cart:
            self.cart.clear()
            self.update_cart_display()

    def update_cart_display(self):
        for item in self.tree_cart.get_children():
            self.tree_cart.delete(item)

        subtotal = 0.0
        for item in self.cart:
            item_tot = item["cantidad"] * item["precio_venta"]
            subtotal += item_tot
            self.tree_cart.insert("", "end", values=(
                item["sku"],
                item["nombre"],
                item["cantidad"],
                format_currency(item["precio_venta"]),
                format_currency(item_tot)
            ))

        iva = subtotal * 0.16
        total = subtotal + iva

        self.lbl_subtotal.config(text=format_currency(subtotal))
        self.lbl_iva.config(text=format_currency(iva))
        self.lbl_total.config(text=format_currency(total))

    def process_checkout(self):
        if not self.cart:
            messagebox.showwarning("Carrito Vacío", "No hay artículos en el carrito para procesar.", parent=self)
            return

        metodo = self.cb_payment.get()
        confirm = messagebox.askyesno(
            "Confirmar Despacho",
            f"¿Desea procesar el despacho por un total de {self.lbl_total.cget('text')}?\n(Método de Pago: {metodo})"
        )
        if not confirm:
            return

        ok, msg, receipt_data = database.process_sale(self.cart, metodo_pago=metodo)

        if ok:
            # Mostrar diálogo con el ticket generado
            ReceiptDialog(self, receipt_data=receipt_data)
            self.cart.clear()
            self.update_cart_display()
            self.search_catalog()

            if hasattr(self.controller, "refresh_dashboard"):
                self.controller.refresh_dashboard()
            if hasattr(self.controller, "refresh_inventory"):
                self.controller.refresh_inventory()
            if hasattr(self.controller, "refresh_movements"):
                self.controller.refresh_movements()
        else:
            messagebox.showerror("Error al procesar", msg, parent=self)


class ReceiptDialog(tk.Toplevel):
    """Diálogo modal que muestra el comprobante / ticket de salida impreso."""
    def __init__(self, parent, receipt_data):
        super().__init__(parent)
        self.title("🧾 Comprobante de Despacho / Venta")
        self.geometry("450x520")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        text_content = generate_receipt_text(receipt_data)

        main = ttk.Frame(self, padding=15)
        main.pack(fill="both", expand=True)

        lbl = ttk.Label(main, text="✅ Operación registrada exitosamente", font=("Helvetica", 11, "bold"), foreground="#15803D")
        lbl.pack(pady=(0, 10))

        text_box = tk.Text(main, wrap="none", font=("Courier New", 9), bg="#F8FAFC", relief="solid", bd=1)
        text_box.insert("1.0", text_content)
        text_box.config(state="disabled")
        text_box.pack(fill="both", expand=True, pady=(0, 10))

        btn_box = ttk.Frame(main)
        btn_box.pack(fill="x")

        btn_copy = ttk.Button(btn_box, text="📋 Copiar al Portapapeles", command=lambda: self._copy_to_clip(text_content))
        btn_copy.pack(side="left", padx=5)

        btn_close = ttk.Button(btn_box, text="Cerrar", command=self.destroy)
        btn_close.pack(side="right", padx=5)

    def _copy_to_clip(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copiado", "Ticket copiado al portapapeles correctamente.", parent=self)
