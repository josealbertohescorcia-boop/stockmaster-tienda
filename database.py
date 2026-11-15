"""
database.py - Módulo de Gestión de Base de Datos SQLite para StockMaster
Sistema de Gestión de Almacén e Inventario para Tienda

Maneja la conexión, creación de tablas, relaciones, transacciones seguras
y precarga de datos iniciales representativos para una tienda de comercio minorista.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "inventario.db")

def get_connection() -> sqlite3.Connection:
    """Retorna una conexión a la base de datos con soporte para llaves foráneas y diccionarios."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Inicializa las tablas relacionales y precarga datos de prueba si la BD está vacía."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla de Categorías
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            descripcion TEXT
        );
    """)

    # Tabla de Proveedores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            contacto TEXT,
            telefono TEXT,
            email TEXT,
            direccion TEXT
        );
    """)

    # Tabla de Productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            id_categoria INTEGER,
            id_proveedor INTEGER,
            precio_compra REAL NOT NULL CHECK(precio_compra >= 0),
            precio_venta REAL NOT NULL CHECK(precio_venta >= 0),
            stock_actual INTEGER NOT NULL DEFAULT 0 CHECK(stock_actual >= 0),
            stock_minimo INTEGER NOT NULL DEFAULT 5 CHECK(stock_minimo >= 0),
            ubicacion TEXT DEFAULT 'Pasillo 1',
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_categoria) REFERENCES categorias(id) ON DELETE SET NULL,
            FOREIGN KEY (id_proveedor) REFERENCES proveedores(id) ON DELETE SET NULL
        );
    """)

    # Tabla de Movimientos de Almacén (Kardex)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_producto INTEGER NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('ENTRADA', 'SALIDA', 'AJUSTE')),
            cantidad INTEGER NOT NULL CHECK(cantidad > 0),
            costo_unitario REAL,
            motivo TEXT,
            fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usuario TEXT DEFAULT 'Administrador',
            FOREIGN KEY (id_producto) REFERENCES productos(id) ON DELETE CASCADE
        );
    """)

    # Tabla de Ventas (Despacho de Tienda)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folio TEXT UNIQUE NOT NULL,
            fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            subtotal REAL NOT NULL,
            iva REAL NOT NULL,
            total REAL NOT NULL,
            metodo_pago TEXT NOT NULL DEFAULT 'Efectivo'
        );
    """)

    # Tabla de Detalle de Venta
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venta INTEGER NOT NULL,
            id_producto INTEGER NOT NULL,
            cantidad INTEGER NOT NULL CHECK(cantidad > 0),
            precio_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (id_venta) REFERENCES ventas(id) ON DELETE CASCADE,
            FOREIGN KEY (id_producto) REFERENCES productos(id) ON DELETE RESTRICT
        );
    """)

    conn.commit()

    # Verificar si se requieren datos semilla
    cursor.execute("SELECT COUNT(*) AS total FROM categorias;")
    if cursor.fetchone()["total"] == 0:
        _seed_initial_data(conn)

    conn.close()

def _seed_initial_data(conn: sqlite3.Connection):
    """Puebla la base de datos con datos de demostración realistas para una tienda."""
    cursor = conn.cursor()

    # Categorías
    categorias = [
        ("Abarrotes y Granos", "Productos básicos de despensa como arroz, frijol y aceite"),
        ("Bebidas y Refrescos", "Aguas embotelladas, jugos, refrescos y energizantes"),
        ("Lácteos y Derivados", "Leche, quesos, yogures y cremas refrigeradas"),
        ("Snacks y Golosinas", "Papas fritas, galletas, chocolates y botanas"),
        ("Limpieza del Hogar", "Detergentes, desinfectantes, esponjas y aromatizantes"),
        ("Higiene Personal", "Jabones corporales, pasta dental y champú")
    ]
    cursor.executemany("INSERT INTO categorias (nombre, descripcion) VALUES (?, ?);", categorias)

    # Proveedores
    proveedores = [
        ("Distribuidora Alimentos del Norte", "Carlos Mendoza", "555-123-4567", "ventas@alimentosnorte.com", "Av. Industrial #104"),
        ("Comercializadora de Bebidas Continental", "Sofía Ramírez", "555-987-6543", "pedidos@continentalbebidas.com", "Zona Franca Bodega 8"),
        ("Lácteos La Campiña S.A.", "Miguel Ángel Castro", "555-456-7890", "mcastro@lacampina.net", "Carretera Km 12"),
        ("Insumos & Limpieza Integral", "Patricia Gómez", "555-789-0123", "atencion@limpiezaintegral.com", "Calle Comercio #45")
    ]
    cursor.executemany("""
        INSERT INTO proveedores (nombre, contacto, telefono, email, direccion)
        VALUES (?, ?, ?, ?, ?);
    """, proveedores)

    # Productos representativos (con SKU, nombre, cat, prov, costo, venta, stock, min, ubicacion)
    # Nota: Algunos se configuran con stock bajo deliberadamente para probar alertas.
    productos = [
        # id_categoria: 1 (Abarrotes), id_proveedor: 1
        ("AB-001", "Arroz Extra Seleccionado 1kg", 1, 1, 18.50, 26.00, 45, 10, "Pasillo 1 - Estante A"),
        ("AB-002", "Frijol Negro Brillante 1kg", 1, 1, 24.00, 34.50, 30, 10, "Pasillo 1 - Estante A"),
        ("AB-003", "Aceite Vegetal Puro 900ml", 1, 1, 32.00, 44.00, 22, 8, "Pasillo 1 - Estante B"),
        ("AB-004", "Atún en Agua en Lata 140g", 1, 1, 14.00, 21.00, 4, 12, "Pasillo 1 - Estante C"), # Stock bajo! (4 <= 12)
        ("AB-005", "Azúcar Estándar 1kg", 1, 1, 22.00, 30.00, 18, 10, "Pasillo 1 - Estante B"),

        # id_categoria: 2 (Bebidas), id_proveedor: 2
        ("BE-101", "Refresco Sabor Cola 2L", 2, 2, 25.00, 36.00, 35, 10, "Pasillo 2 - Refrigerador 1"),
        ("BE-102", "Agua Mineral Natural 1.5L", 2, 2, 10.00, 16.50, 50, 15, "Pasillo 2 - Refrigerador 2"),
        ("BE-103", "Jugo de Naranja 100% 1L", 2, 2, 17.00, 25.00, 3, 8, "Pasillo 2 - Refrigerador 1"), # Stock bajo! (3 <= 8)

        # id_categoria: 3 (Lácteos), id_proveedor: 3
        ("LA-201", "Leche Entera Pasteurizada 1L", 3, 3, 19.00, 27.50, 28, 12, "Pasillo 3 - Nevera 1"),
        ("LA-202", "Queso Panela Fresco 400g", 3, 3, 42.00, 60.00, 14, 5, "Pasillo 3 - Nevera 1"),
        ("LA-203", "Yogurt Natural Bebible 1kg", 3, 3, 28.00, 39.00, 11, 6, "Pasillo 3 - Nevera 2"),

        # id_categoria: 4 (Snacks), id_proveedor: 1
        ("SN-301", "Papas Fritas Onduladas Sal 160g", 4, 1, 15.00, 24.00, 40, 10, "Pasillo 4 - Gondola 1"),
        ("SN-302", "Galletas Dulces con Chispas 250g", 4, 1, 16.50, 25.00, 25, 8, "Pasillo 4 - Gondola 2"),

        # id_categoria: 5 (Limpieza), id_proveedor: 4
        ("LI-401", "Detergente Multiusos en Polvo 1kg", 5, 4, 26.00, 38.00, 20, 8, "Pasillo 5 - Estante A"),
        ("LI-402", "Cloro Desinfectante Líquido 1L", 5, 4, 11.50, 18.00, 32, 10, "Pasillo 5 - Estante B"),

        # id_categoria: 6 (Higiene), id_proveedor: 4
        ("HI-501", "Jabón de Tocador Humectante 135g", 6, 4, 9.50, 15.00, 2, 10, "Pasillo 6 - Estante A") # Stock bajo! (2 <= 10)
    ]

    cursor.executemany("""
        INSERT INTO productos (sku, nombre, id_categoria, id_proveedor, precio_compra, precio_venta, stock_actual, stock_minimo, ubicacion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, productos)

    # Registrar movimientos iniciales correspondientes a la carga inicial
    for prod in productos:
        cursor.execute("SELECT id FROM productos WHERE sku = ?;", (prod[0],))
        row = cursor.fetchone()
        if row:
            p_id = row["id"]
            cursor.execute("""
                INSERT INTO movimientos (id_producto, tipo, cantidad, costo_unitario, motivo, usuario)
                VALUES (?, 'ENTRADA', ?, ?, 'Inventario Inicial del Sistema', 'Sistema');
            """, (p_id, prod[6], prod[4]))

    conn.commit()


# ==========================================
# MÓDULO DE PRODUCTOS (CRUD)
# ==========================================

def get_products(search_text: str = "", category_id: Optional[int] = None, only_low_stock: bool = False) -> List[Dict[str, Any]]:
    """Obtiene el listado de productos con filtros opcionales de búsqueda, categoría y stock bajo."""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            p.id, p.sku, p.nombre, p.precio_compra, p.precio_venta, 
            p.stock_actual, p.stock_minimo, p.ubicacion, p.fecha_registro,
            c.id AS categoria_id, c.nombre AS categoria_nombre,
            pr.id AS proveedor_id, pr.nombre AS proveedor_nombre
        FROM productos p
        LEFT JOIN categorias c ON p.id_categoria = c.id
        LEFT JOIN proveedores pr ON p.id_proveedor = pr.id
        WHERE 1=1
    """
    params = []

    if search_text:
        term = f"%{search_text.strip()}%"
        query += " AND (p.nombre LIKE ? OR p.sku LIKE ? OR p.ubicacion LIKE ?)"
        params.extend([term, term, term])

    if category_id:
        query += " AND p.id_categoria = ?"
        params.append(category_id)

    if only_low_stock:
        query += " AND p.stock_actual <= p.stock_minimo"

    query += " ORDER BY p.id DESC;"

    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    """Busca un producto por su clave primaria."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            p.*, 
            c.nombre AS categoria_nombre,
            pr.nombre AS proveedor_nombre
        FROM productos p
        LEFT JOIN categorias c ON p.id_categoria = c.id
        LEFT JOIN proveedores pr ON p.id_proveedor = pr.id
        WHERE p.id = ?;
    """, (product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_product_by_sku(sku: str) -> Optional[Dict[str, Any]]:
    """Busca un producto por su código SKU."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE UPPER(sku) = UPPER(?);", (sku.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_product(sku: str, nombre: str, id_categoria: Optional[int], id_proveedor: Optional[int],
                   precio_compra: float, precio_venta: float, stock_inicial: int,
                   stock_minimo: int, ubicacion: str) -> Tuple[bool, str]:
    """Crea un nuevo producto en el catálogo y registra su movimiento inicial si tiene stock."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO productos (sku, nombre, id_categoria, id_proveedor, precio_compra, precio_venta, stock_actual, stock_minimo, ubicacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (sku.strip().upper(), nombre.strip(), id_categoria, id_proveedor, precio_compra, precio_venta, stock_inicial, stock_minimo, ubicacion.strip()))
        
        prod_id = cursor.lastrowid
        if stock_inicial > 0:
            cursor.execute("""
                INSERT INTO movimientos (id_producto, tipo, cantidad, costo_unitario, motivo, usuario)
                VALUES (?, 'ENTRADA', ?, ?, 'Stock Inicial de Creación', 'Administrador');
            """, (prod_id, stock_inicial, precio_compra))

        conn.commit()
        return True, "Producto registrado exitosamente."
    except sqlite3.IntegrityError as e:
        conn.rollback()
        if "UNIQUE constraint failed: productos.sku" in str(e):
            return False, f"El código SKU '{sku}' ya está registrado con otro producto."
        return False, f"Error de integridad en los datos: {e}"
    except Exception as e:
        conn.rollback()
        return False, f"Error al guardar producto: {e}"
    finally:
        conn.close()

def update_product(product_id: int, sku: str, nombre: str, id_categoria: Optional[int],
                   id_proveedor: Optional[int], precio_compra: float, precio_venta: float,
                   stock_minimo: int, ubicacion: str) -> Tuple[bool, str]:
    """Actualiza los datos informativos y de precios de un producto."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE productos 
            SET sku = ?, nombre = ?, id_categoria = ?, id_proveedor = ?,
                precio_compra = ?, precio_venta = ?, stock_minimo = ?, ubicacion = ?
            WHERE id = ?;
        """, (sku.strip().upper(), nombre.strip(), id_categoria, id_proveedor,
              precio_compra, precio_venta, stock_minimo, ubicacion.strip(), product_id))
        conn.commit()
        return True, "Producto actualizado correctamente."
    except sqlite3.IntegrityError as e:
        conn.rollback()
        return False, f"El código SKU '{sku}' ya pertenece a otro producto."
    except Exception as e:
        conn.rollback()
        return False, f"Error al actualizar producto: {e}"
    finally:
        conn.close()

def delete_product(product_id: int) -> Tuple[bool, str]:
    """Elimina un producto si no está referenciado en ventas históricas."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Validar si tiene ventas asociadas
        cursor.execute("SELECT COUNT(*) AS total FROM detalle_ventas WHERE id_producto = ?;", (product_id,))
        if cursor.fetchone()["total"] > 0:
            return False, "No se puede eliminar el producto porque tiene ventas históricas asociadas (integridad contable)."

        cursor.execute("DELETE FROM productos WHERE id = ?;", (product_id,))
        conn.commit()
        return True, "Producto eliminado correctamente."
    except Exception as e:
        conn.rollback()
        return False, f"Error al eliminar producto: {e}"
    finally:
        conn.close()


# ==========================================
# MÓDULO DE MOVIMIENTOS Y KARDEX (ALMACÉN)
# ==========================================

def register_movement(product_id: int, tipo: str, cantidad: int, costo_unitario: float,
                      motivo: str, usuario: str = "Administrador") -> Tuple[bool, str]:
    """
    Registra una entrada, salida o ajuste en el almacén de manera transaccional,
    actualizando inmediatamente el stock del producto.
    """
    if cantidad <= 0:
        return False, "La cantidad del movimiento debe ser mayor a cero."

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Obtener stock actual
        cursor.execute("SELECT stock_actual, nombre FROM productos WHERE id = ?;", (product_id,))
        prod = cursor.fetchone()
        if not prod:
            return False, "El producto especificado no existe."

        stock_actual = prod["stock_actual"]
        nombre = prod["nombre"]

        if tipo == "ENTRADA":
            nuevo_stock = stock_actual + cantidad
        elif tipo == "SALIDA":
            if cantidad > stock_actual:
                return False, f"Stock insuficiente para '{nombre}'. Disponible: {stock_actual}, solicitado: {cantidad}."
            nuevo_stock = stock_actual - cantidad
        elif tipo == "AJUSTE":
            nuevo_stock = cantidad  # En ajuste, la cantidad representa el conteo físico real
        else:
            return False, f"Tipo de movimiento '{tipo}' no reconocido."

        # Registrar el movimiento
        cursor.execute("""
            INSERT INTO movimientos (id_producto, tipo, cantidad, costo_unitario, motivo, usuario)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (product_id, tipo, cantidad, costo_unitario, motivo.strip(), usuario))

        # Actualizar stock del producto
        cursor.execute("UPDATE productos SET stock_actual = ? WHERE id = ?;", (nuevo_stock, product_id))

        conn.commit()
        return True, f"Movimiento registrado. Nuevo stock de '{nombre}': {nuevo_stock} unidades."
    except Exception as e:
        conn.rollback()
        return False, f"Error al procesar movimiento de almacén: {e}"
    finally:
        conn.close()

def get_movements(limit: int = 200, product_id: Optional[int] = None, tipo: Optional[str] = None) -> List[Dict[str, Any]]:
    """Obtiene el historial de movimientos de almacén con información detallada del producto."""
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT 
            m.id, m.tipo, m.cantidad, m.costo_unitario, m.motivo, 
            m.fecha_movimiento, m.usuario,
            p.sku, p.nombre AS producto_nombre, p.stock_actual
        FROM movimientos m
        JOIN productos p ON m.id_producto = p.id
        WHERE 1=1
    """
    params = []
    if product_id:
        query += " AND m.id_producto = ?"
        params.append(product_id)
    if tipo and tipo != "TODOS":
        query += " AND m.tipo = ?"
        params.append(tipo)

    query += " ORDER BY m.id DESC LIMIT ?;"
    params.append(limit)

    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


# ==========================================
# MÓDULO DE VENTAS / DESPACHO RÁPIDO
# ==========================================

def process_sale(cart_items: List[Dict[str, Any]], metodo_pago: str = "Efectivo", iva_tasa: float = 0.16) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Procesa una venta completa en una sola transacción atómica:
    - Valida disponibilidad de stock para cada artículo.
    - Descuenta existencias en productos.
    - Genera movimientos de almacén tipo 'SALIDA'.
    - Registra la cabecera de la venta y sus detalles.
    """
    if not cart_items:
        return False, "El carrito de despacho está vacío.", None

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Validar existencias
        for item in cart_items:
            cursor.execute("SELECT stock_actual, nombre FROM productos WHERE id = ?;", (item["id"],))
            prod = cursor.fetchone()
            if not prod:
                raise ValueError(f"Producto con ID {item['id']} no encontrado.")
            if prod["stock_actual"] < item["cantidad"]:
                raise ValueError(f"Stock insuficiente para '{prod['nombre']}'. Disponible: {prod['stock_actual']}, Requerido: {item['cantidad']}.")

        # Calcular totales
        subtotal = sum(item["precio_venta"] * item["cantidad"] for item in cart_items)
        iva = subtotal * iva_tasa
        total = subtotal + iva
        folio = f"VTA-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Insertar venta
        cursor.execute("""
            INSERT INTO ventas (folio, subtotal, iva, total, metodo_pago)
            VALUES (?, ?, ?, ?, ?);
        """, (folio, subtotal, iva, total, metodo_pago))
        venta_id = cursor.lastrowid

        # Insertar detalles, descontar stock y generar movimientos
        for item in cart_items:
            item_subtotal = item["precio_venta"] * item["cantidad"]
            cursor.execute("""
                INSERT INTO detalle_ventas (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?);
            """, (venta_id, item["id"], item["cantidad"], item["precio_venta"], item_subtotal))

            # Descontar stock
            cursor.execute("""
                UPDATE productos 
                SET stock_actual = stock_actual - ? 
                WHERE id = ?;
            """, (item["cantidad"], item["id"]))

            # Registrar movimiento de salida
            cursor.execute("""
                INSERT INTO movimientos (id_producto, tipo, cantidad, costo_unitario, motivo, usuario)
                VALUES (?, 'SALIDA', ?, ?, ?, 'Cajero/Ventas');
            """, (item["id"], item["cantidad"], item["precio_compra"], f"Venta de mostrador Folio: {folio}"))

        conn.commit()

        receipt_data = {
            "folio": folio,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "subtotal": subtotal,
            "iva": iva,
            "total": total,
            "metodo_pago": metodo_pago,
            "items": cart_items
        }
        return True, f"Venta {folio} registrada exitosamente.", receipt_data

    except ValueError as ve:
        conn.rollback()
        return False, str(ve), None
    except Exception as e:
        conn.rollback()
        return False, f"Error al procesar la venta: {e}", None
    finally:
        conn.close()

def get_recent_sales(limit: int = 50) -> List[Dict[str, Any]]:
    """Devuelve las últimas ventas registradas."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.*, COUNT(dv.id) AS total_articulos
        FROM ventas v
        LEFT JOIN detalle_ventas dv ON v.id = dv.id_venta
        GROUP BY v.id
        ORDER BY v.id DESC
        LIMIT ?;
    """, (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


# ==========================================
# MÓDULO DE CATEGORÍAS Y PROVEEDORES
# ==========================================

def get_categories() -> List[Dict[str, Any]]:
    """Obtiene todas las categorías registradas."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categorias ORDER BY nombre ASC;")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def add_category(nombre: str, descripcion: str = "") -> Tuple[bool, str]:
    """Agrega una nueva categoría al sistema."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categorias (nombre, descripcion) VALUES (?, ?);", (nombre.strip(), descripcion.strip()))
        conn.commit()
        return True, "Categoría agregada exitosamente."
    except sqlite3.IntegrityError:
        return False, "Ya existe una categoría con ese nombre."
    except Exception as e:
        return False, f"Error al agregar categoría: {e}"
    finally:
        conn.close()

def get_suppliers() -> List[Dict[str, Any]]:
    """Obtiene todos los proveedores registrados."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM proveedores ORDER BY nombre ASC;")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def add_supplier(nombre: str, contacto: str = "", telefono: str = "", email: str = "", direccion: str = "") -> Tuple[bool, str]:
    """Registra un nuevo proveedor."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO proveedores (nombre, contacto, telefono, email, direccion)
            VALUES (?, ?, ?, ?, ?);
        """, (nombre.strip(), contacto.strip(), telefono.strip(), email.strip(), direccion.strip()))
        conn.commit()
        return True, "Proveedor registrado exitosamente."
    except Exception as e:
        return False, f"Error al registrar proveedor: {e}"
    finally:
        conn.close()


# ==========================================
# MÉTRICAS Y DASHBOARD
# ==========================================

def get_dashboard_metrics() -> Dict[str, Any]:
    """Calcula indicadores clave de rendimiento (KPIs) para la tienda y el almacén."""
    conn = get_connection()
    cursor = conn.cursor()

    # Total de productos y cantidades
    cursor.execute("""
        SELECT 
            COUNT(*) AS total_productos,
            COALESCE(SUM(stock_actual), 0) AS total_unidades,
            COALESCE(SUM(stock_actual * precio_compra), 0.0) AS valor_almacen_costo,
            COALESCE(SUM(stock_actual * precio_venta), 0.0) AS valor_almacen_venta,
            COUNT(CASE WHEN stock_actual <= stock_minimo THEN 1 END) AS alertas_stock_bajo
        FROM productos;
    """)
    prod_metrics = dict(cursor.fetchone())

    # Total proveedores
    cursor.execute("SELECT COUNT(*) AS total_proveedores FROM proveedores;")
    prod_metrics["total_proveedores"] = cursor.fetchone()["total_proveedores"]

    # Total categorías
    cursor.execute("SELECT COUNT(*) AS total_categorias FROM categorias;")
    prod_metrics["total_categorias"] = cursor.fetchone()["total_categorias"]

    # Ventas del día actual
    cursor.execute("""
        SELECT 
            COUNT(*) AS total_ventas_hoy,
            COALESCE(SUM(total), 0.0) AS ingresos_hoy
        FROM ventas
        WHERE DATE(fecha_venta) = DATE('now', 'localtime');
    """)
    ventas_hoy = dict(cursor.fetchone())
    prod_metrics.update(ventas_hoy)

    conn.close()
    return prod_metrics

def get_low_stock_alerts() -> List[Dict[str, Any]]:
    """Obtiene los productos que han alcanzado o caído por debajo del umbral mínimo."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            p.sku, p.nombre, p.stock_actual, p.stock_minimo, p.ubicacion,
            c.nombre AS categoria, pr.nombre AS proveedor
        FROM productos p
        LEFT JOIN categorias c ON p.id_categoria = c.id
        LEFT JOIN proveedores pr ON p.id_proveedor = pr.id
        WHERE p.stock_actual <= p.stock_minimo
        ORDER BY (p.stock_actual - p.stock_minimo) ASC, p.stock_actual ASC;
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows
