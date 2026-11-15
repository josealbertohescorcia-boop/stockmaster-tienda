"""
suppliers_view.py - Vista de Gestión de Proveedores y Categorías para StockMaster
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database

class SuppliersView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(padding=15)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))

        ttk.Label(header, text="👥 Directorio de Proveedores y Categorías", font=("Helvetica", 15, "bold")).pack(side="left")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        # Tab 1: Proveedores
        self.tab_suppliers = ttk.Frame(notebook, padding=10)
        notebook.add(self.tab_suppliers, text="🏢 Proveedores de Almacén")
        self._build_suppliers_tab()

        # Tab 2: Categorías
        self.tab_categories = ttk.Frame(notebook, padding=10)
        notebook.add(self.tab_categories, text="🏷️ Categorías de Catálogo")
        self._build_categories_tab()

    def _build_suppliers_tab(self):
        top_bar = ttk.Frame(self.tab_suppliers)
        top_bar.pack(fill="x", pady=(0, 10))

        btn_new_prov = ttk.Button(top_bar, text="➕ Registrar Proveedor", command=self.open_new_supplier_dialog)
        btn_new_prov.pack(side="left")

        cols = ("id", "nombre", "contacto", "telefono", "email", "direccion")
        self.tree_supp = ttk.Treeview(self.tab_suppliers, columns=cols, show="headings", selectmode="browse")
        self.tree_supp.heading("id", text="ID")
        self.tree_supp.heading("nombre", text="Empresa / Razón Social")
        self.tree_supp.heading("contacto", text="Persona de Contacto")
        self.tree_supp.heading("telefono", text="Teléfono")
        self.tree_supp.heading("email", text="Correo Electrónico")
        self.tree_supp.heading("direccion", text="Dirección / Ubicación")

        self.tree_supp.column("id", width=45, anchor="center")
        self.tree_supp.column("nombre", width=220, anchor="w")
        self.tree_supp.column("contacto", width=160, anchor="w")
        self.tree_supp.column("telefono", width=120, anchor="center")
        self.tree_supp.column("email", width=200, anchor="w")
        self.tree_supp.column("direccion", width=200, anchor="w")

        scroll = ttk.Scrollbar(self.tab_suppliers, orient="vertical", command=self.tree_supp.yview)
        self.tree_supp.configure(yscrollcommand=scroll.set)

        self.tree_supp.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def _build_categories_tab(self):
        top_bar = ttk.Frame(self.tab_categories)
        top_bar.pack(fill="x", pady=(0, 10))

        btn_new_cat = ttk.Button(top_bar, text="➕ Nueva Categoría", command=self.open_new_category_dialog)
        btn_new_cat.pack(side="left")

        cols = ("id", "nombre", "descripcion")
        self.tree_cat = ttk.Treeview(self.tab_categories, columns=cols, show="headings", selectmode="browse")
        self.tree_cat.heading("id", text="ID")
        self.tree_cat.heading("nombre", text="Nombre de la Categoría")
        self.tree_cat.heading("descripcion", text="Descripción / Familia de Productos")

        self.tree_cat.column("id", width=50, anchor="center")
        self.tree_cat.column("nombre", width=240, anchor="w")
        self.tree_cat.column("descripcion", width=450, anchor="w")

        scroll = ttk.Scrollbar(self.tab_categories, orient="vertical", command=self.tree_cat.yview)
        self.tree_cat.configure(yscrollcommand=scroll.set)

        self.tree_cat.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def load_suppliers(self):
        supps = database.get_suppliers()
        for item in self.tree_supp.get_children():
            self.tree_supp.delete(item)
        for s in supps:
            self.tree_supp.insert("", "end", values=(
                s["id"], s["nombre"], s["contacto"] or "-", s["telefono"] or "-", s["email"] or "-", s["direccion"] or "-"
            ))

    def load_categories(self):
        cats = database.get_categories()
        for item in self.tree_cat.get_children():
            self.tree_cat.delete(item)
        for c in cats:
            self.tree_cat.insert("", "end", values=(
                c["id"], c["nombre"], c["descripcion"] or "-"
            ))

    def refresh(self):
        self.load_suppliers()
        self.load_categories()

    def open_new_supplier_dialog(self):
        SupplierDialog(self, on_save=self.refresh)

    def open_new_category_dialog(self):
        CategoryDialog(self, on_save=self.refresh)


class SupplierDialog(tk.Toplevel):
    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        self.title("Registrar Nuevo Proveedor")
        self.geometry("440x360")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.on_save = on_save

        main = ttk.Frame(self, padding=20)
        main.pack(fill="both", expand=True)

        pad = {"padx": 10, "pady": 6}

        ttk.Label(main, text="Nombre / Empresa: *").grid(row=0, column=0, sticky="w", **pad)
        self.e_nombre = ttk.Entry(main, width=28)
        self.e_nombre.grid(row=0, column=1, sticky="w", **pad)

        ttk.Label(main, text="Persona de Contacto:").grid(row=1, column=0, sticky="w", **pad)
        self.e_contacto = ttk.Entry(main, width=28)
        self.e_contacto.grid(row=1, column=1, sticky="w", **pad)

        ttk.Label(main, text="Teléfono:").grid(row=2, column=0, sticky="w", **pad)
        self.e_tel = ttk.Entry(main, width=28)
        self.e_tel.grid(row=2, column=1, sticky="w", **pad)

        ttk.Label(main, text="Correo Electrónico:").grid(row=3, column=0, sticky="w", **pad)
        self.e_email = ttk.Entry(main, width=28)
        self.e_email.grid(row=3, column=1, sticky="w", **pad)

        ttk.Label(main, text="Dirección:").grid(row=4, column=0, sticky="w", **pad)
        self.e_dir = ttk.Entry(main, width=28)
        self.e_dir.grid(row=4, column=1, sticky="w", **pad)

        btn_box = ttk.Frame(main)
        btn_box.grid(row=5, column=0, columnspan=2, pady=(20, 0))

        btn_save = ttk.Button(btn_box, text="Guardar Proveedor", command=self.save)
        btn_save.pack(side="left", padx=10)

        btn_cancel = ttk.Button(btn_box, text="Cancelar", command=self.destroy)
        btn_cancel.pack(side="left", padx=10)

    def save(self):
        nom = self.e_nombre.get().strip()
        if not nom:
            messagebox.showwarning("Atención", "El nombre del proveedor es obligatorio.", parent=self)
            return
        ok, msg = database.add_supplier(nom, self.e_contacto.get().strip(), self.e_tel.get().strip(), self.e_email.get().strip(), self.e_dir.get().strip())
        if ok:
            messagebox.showinfo("Éxito", msg, parent=self)
            if self.on_save:
                self.on_save()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)


class CategoryDialog(tk.Toplevel):
    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        self.title("Nueva Categoría")
        self.geometry("400x240")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.on_save = on_save

        main = ttk.Frame(self, padding=20)
        main.pack(fill="both", expand=True)

        pad = {"padx": 10, "pady": 6}

        ttk.Label(main, text="Nombre Categoría: *").grid(row=0, column=0, sticky="w", **pad)
        self.e_nombre = ttk.Entry(main, width=24)
        self.e_nombre.grid(row=0, column=1, sticky="w", **pad)

        ttk.Label(main, text="Descripción:").grid(row=1, column=0, sticky="w", **pad)
        self.e_desc = ttk.Entry(main, width=24)
        self.e_desc.grid(row=1, column=1, sticky="w", **pad)

        btn_box = ttk.Frame(main)
        btn_box.grid(row=2, column=0, columnspan=2, pady=(20, 0))

        btn_save = ttk.Button(btn_box, text="Guardar Categoría", command=self.save)
        btn_save.pack(side="left", padx=10)

        btn_cancel = ttk.Button(btn_box, text="Cancelar", command=self.destroy)
        btn_cancel.pack(side="left", padx=10)

    def save(self):
        nom = self.e_nombre.get().strip()
        if not nom:
            messagebox.showwarning("Atención", "El nombre de la categoría es obligatorio.", parent=self)
            return
        ok, msg = database.add_category(nom, self.e_desc.get().strip())
        if ok:
            messagebox.showinfo("Éxito", msg, parent=self)
            if self.on_save:
                self.on_save()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)
