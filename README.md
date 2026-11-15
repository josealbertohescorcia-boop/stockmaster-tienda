# 🏪 StockMaster — Sistema de Gestión de Almacén e Inventario para Tienda

> **Proyecto Final de Asignatura**  
> **Carrera:** Ingeniería en Sistemas Computacionales / Software / Informática  
> **Asignatura:** Desarrollo de Software / Programación  
> **Fecha de Entrega:** Noviembre 2026  

---

## 👥 Integrantes del Equipo
*Cada integrante del equipo entrega este mismo repositorio y el documento PDF correspondiente:*

| Nombre Completo | Matrícula / ID | Rol / Responsabilidad |
| :--- | :---: | :--- |
| **Escorcia, José Alberto** | `Estudiante` | Arquitectura, Backend & Base de Datos SQLite |
| *[Compañero de equipo 2]* | `[Matrícula 2]` | Interfaz Gráfica (Tkinter/TTk) & Módulo POS |
| *[Compañero de equipo 3]* | `[Matrícula 3]` | Módulo de Kardex, Pruebas & Documentación |

*Docente Titular:* **[Profesor / Titular de Asignatura]**  
*Enlace al Repositorio de GitHub:* `https://github.com/josealbertohescorcia-boop/stockmaster-tienda`

---

## 📋 Resumen del Proyecto

**StockMaster** es una aplicación de escritorio diseñada para modernizar, automatizar y optimizar la administración de almacén e inventario en comercios minoristas (tiendas de abarrotes, minimarkets, bodegas o depósitos).

El sistema sustituye las bitácoras manuales en papel y las hojas de cálculo propensas a errores por un software robusto con persistencia en **SQLite**, arquitectura desacoplada y una interfaz gráfica intuitiva desarrollada en **Python (Tkinter)**. Garantiza la trazabilidad absoluta de las existencias mediante un sistema de **Kardex (Entradas, Salidas y Ajustes)**, emite alertas automáticas de reabastecimiento antes de llegar a desabasto, permite despachos rápidos tipo Punto de Venta (POS) con cálculo de impuestos y emite comprobantes digitales.

---

## ✨ Características Principales

### 1. 📊 Panel de Control y Resumen Ejecutivo (Dashboard)
- **Tarjetas KPI en tiempo real:**
  - Total de productos y unidades registradas.
  - Valor total del almacén al costo de adquisición.
  - Alertas activas de productos con existencia crítica.
  - Ventas y recaudación del día en curso.
- **Acceso directo a operaciones frecuentes:** alta rápida de producto, recepción de mercancía y despacho.
- **Tabla interactiva de stock bajo:** prioriza los artículos que requieren compra urgente.

### 2. 📦 Catálogo y Control de Inventario (CRUD Completo)
- Registro, edición y baja de productos con validaciones de integridad.
- Atributos detallados: Código SKU único, nombre, categoría, proveedor sugerido, costo de compra, precio de venta, stock actual, stock mínimo (punto de reorden) y ubicación física en estantería/pasillo.
- Búsqueda en tiempo real (por SKU, nombre o ubicación).
- Filtros por categoría y selector de productos con existencia crítica.
- Códigos de color visuales: 🟢 Normal, 🟡 Stock Bajo, 🔴 Agotado.

### 3. 🔄 Movimientos de Almacén y Kardex
- **Entradas de almacén:** registro de compras y reposición a proveedores; actualiza el costo y suma existencias automáticamente.
- **Salidas de almacén:** control estricto de mermas, productos caducados, daños o autoconsumo con validación preventiva de stock negativo.
- **Ajustes de inventario:** registro de conteos físicos periódicos con justificación auditable.
- Historial completo con fecha, hora, tipo de movimiento, cantidad, costo unitario, motivo y usuario responsable.

### 4. 🛒 Despacho Rápido y Punto de Venta (POS)
- Búsqueda instantánea de mercancía por código o descripción.
- Carrito de despacho con validación de inventario en tiempo real.
- Cálculo automático de subtotal, IVA (16%) y total a pagar.
- Múltiples métodos de pago: Efectivo, Tarjeta de Débito, Tarjeta de Crédito, Transferencia.
- **Generación de Ticket / Comprobante de Salida** con opción de copiado directo y guardado.

### 5. 👥 Proveedores y Categorías
- Directorio de proveedores con datos de contacto, teléfono, correo y domicilio.
- Gestión de categorías de productos para segmentación comercial.

### 6. 📈 Reportes Financieros y Exportación
- Valuación económica del almacén (costo vs. precio de venta) y margen de ganancia bruta proyectado.
- Historial detallado de ventas y despachos.
- **Exportación en un clic a formato CSV (compatible con Microsoft Excel)** para Catálogo de Inventario, Kardex de Movimientos y Ventas.

---

## 🛠️ Tecnologías y Requisitos

| Componente | Tecnología / Estándar | Justificación Técnica |
| :--- | :--- | :--- |
| **Lenguaje** | Python 3.10 o superior | Multiplataforma, sintaxis limpia y mantenible |
| **Interfaz Gráfica** | `tkinter` y `tkinter.ttk` | Interfaz nativa de escritorio sin requerir instalación de frameworks pesados |
| **Persistencia** | SQLite 3 | Base de datos relacional embebida con soporte de transacciones ACID y llaves foráneas |
| **Exportación** | Módulo `csv` (codificación UTF-8 con BOM) | Compatibilidad inmediata con Microsoft Excel y hojas de cálculo |
| **Dependencias Externas** | **Ninguna (0 dependencias pip)** | Ejecutable inmediatamente en cualquier ordenador con Python estándar |

---

## 🚀 Guía de Instalación y Ejecución Paso a Paso

### 1. Clonar el repositorio
```bash
git clone https://github.com/[TU_USUARIO]/[NOMBRE_DEL_REPOSITORIO].git
cd sistema_almacen_tienda
```

### 2. Verificar versión de Python
Asegúrate de contar con Python 3 instalado:
```bash
python --version
```
*(Debe responder Python 3.10 o superior).*

### 3. Ejecutar la aplicación
No es necesario crear entornos virtuales complejos ni ejecutar `pip install`, ya que utiliza la biblioteca estándar de Python:
```bash
python main.py
```

> **Nota:** La primera vez que se ejecuta, el sistema crea automáticamente la base de datos `data/inventario.db` y la precarga con categorías, proveedores y 16 productos reales para facilitar la evaluación inmediata del prototipo.

---

## 📁 Estructura del Proyecto

```text
sistema_almacen_tienda/
│
├── main.py                     # Punto de entrada y arranque del software
├── database.py                 # Conexión SQLite, esquemas DDL y operaciones CRUD
│
├── ui/                         # Módulo de Interfaz Gráfica (Tkinter)
│   ├── __init__.py
│   ├── main_window.py          # Ventana principal, navegación y barra lateral
│   ├── dashboard_view.py       # Vista del panel de métricas y alertas
│   ├── inventory_view.py       # Catálogo de productos, filtros y diálogo modal
│   ├── movements_view.py       # Registro de entradas, salidas y Kardex
│   ├── pos_view.py             # Módulo de despacho rápido, carrito y ticket
│   ├── suppliers_view.py       # Directorio de proveedores y categorías
│   └── reports_view.py         # Análisis de márgenes y centro de exportación
│
├── utils/                      # Módulo de utilerías y soporte
│   ├── __init__.py
│   └── helpers.py              # Formateo de moneda, fechas, CSV y tickets
│
├── data/                       # Almacenamiento local de la base de datos
│   └── inventario.db           # Base de datos SQLite (se genera en el primer inicio)
│
├── docs/                       # Documentación académica de entrega
│   ├── ProyectoFinal_ApellidoNombre.pdf   # Documento formal del proyecto
│   └── ProyectoFinal_Documento.html       # Fuente HTML imprimible
│
├── .gitignore                  # Exclusión de archivos compilados y temporales
└── README.md                   # Manual técnico y de usuario del repositorio
```

---

## 🤖 Declaración sobre el Uso de Inteligencia Artificial

En cumplimiento con los lineamientos éticos y académicos de la entrega, declaramos de manera explícita y transparente la utilización de herramientas de Inteligencia Artificial durante el desarrollo de este proyecto:

* **Herramienta(s) Utilizada(s):** Google Antigravity (asistente de código basado en modelos Gemini).
* **Propósito y Tareas Específicas Realizadas con IA:**
  1. *Arquitectura de Software:* Asistencia en la modularización del patrón Modelo-Vista-Controlador (MVC) y diseño del esquema relacional SQLite (definición de restricciones `CHECK`, llaves foráneas e integridad referencial).
  2. *Generación de Datos de Prueba:* Creación del conjunto inicial de datos representativos de una tienda de abarrotes para simular escenarios reales de baja existencia y Kardex.
  3. *Optimización de Interfaz:* Apoyo en la configuración de temas, tipografías y paletas de color en `tkinter.ttk`.
  4. *Redacción de Documentación:* Apoyo en la estructura del manual técnico, especificación de requerimientos y formato del documento PDF académico.
* **Supervisión y Validación Humana:**
  Todo el código generado fue revisado minuciosamente, integrado, probado de manera interactiva y depurado por el equipo de estudiantes. Se validaron manualmente las transacciones de descuento de inventario, la prevención de stock negativo y la consistencia matemática de los totales e impuestos generados en las ventas.

---

## 🔒 Verificación de Seguridad y Buenas Prácticas

Previo a la publicación de este repositorio se realizaron las siguientes verificaciones:
- [x] **Cero Credenciales:** No existen contraseñas, tokens de autenticación ni cadenas de conexión con credenciales reales en el código.
- [x] **Cero Llaves de API:** La aplicación es 100% local y no utiliza ni expone claves privadas de servicios de terceros.
- [x] **Privacidad de Datos:** Los nombres de proveedores, personas de contacto, direcciones y teléfonos incluidos son enteramente ficticios y de carácter ilustrativo para fines académicos.
- [x] **Archivo `.gitignore` Configurado:** Se previene la subida accidental de archivos temporales, binarios de entorno y cachés de Python (`__pycache__`).

---

## 📄 Licencia

Este proyecto fue desarrollado con fines educativos para la entrega de la asignatura. Se distribuye bajo los términos de la **Licencia MIT**, permitiendo su uso, estudio y modificación académica.
