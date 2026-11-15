"""
helpers.py - Utilidades, formateadores y exportadores para StockMaster
"""

import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

def format_currency(amount: Optional[float]) -> str:
    """Formatea una cantidad numérica a formato de moneda con dos decimales ($ #,##0.00)."""
    if amount is None:
        return "$0.00"
    try:
        return f"${float(amount):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"

def format_date(date_str: Optional[str]) -> str:
    """Convierte cadenas de fecha ISO/SQLite a un formato amigable 'DD/MM/AAAA HH:MM'."""
    if not date_str:
        return "-"
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(date_str)

def export_inventory_csv(products: List[Dict[str, Any]], filepath: str) -> bool:
    """Exporta el catálogo de productos actual a un archivo CSV codificado para Excel."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            # Encabezados
            writer.writerow([
                "ID", "SKU / Código", "Nombre del Producto", "Categoría",
                "Proveedor", "Costo de Compra", "Precio de Venta",
                "Stock Actual", "Stock Mínimo", "Valor en Almacén", "Ubicación"
            ])
            for p in products:
                costo = p.get("precio_compra", 0.0)
                stock = p.get("stock_actual", 0)
                valor_total = costo * stock
                writer.writerow([
                    p.get("id"),
                    p.get("sku"),
                    p.get("nombre"),
                    p.get("categoria_nombre") or "Sin categoría",
                    p.get("proveedor_nombre") or "Sin proveedor",
                    f"{costo:.2f}",
                    f"{p.get('precio_venta', 0.0):.2f}",
                    stock,
                    p.get("stock_minimo", 0),
                    f"{valor_total:.2f}",
                    p.get("ubicacion", "")
                ])
        return True
    except Exception as e:
        print(f"Error exportando inventario a CSV: {e}")
        return False

def export_movements_csv(movements: List[Dict[str, Any]], filepath: str) -> bool:
    """Exporta el historial de movimientos a un archivo CSV."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([
                "ID", "Fecha", "Tipo", "SKU", "Producto",
                "Cantidad", "Costo Unitario", "Motivo / Detalle", "Usuario"
            ])
            for m in movements:
                writer.writerow([
                    m.get("id"),
                    m.get("fecha_movimiento"),
                    m.get("tipo"),
                    m.get("sku"),
                    m.get("producto_nombre"),
                    m.get("cantidad"),
                    f"{m.get('costo_unitario', 0.0) or 0.0:.2f}",
                    m.get("motivo"),
                    m.get("usuario")
                ])
        return True
    except Exception as e:
        print(f"Error exportando movimientos: {e}")
        return False

def generate_receipt_text(receipt_data: Dict[str, Any], store_name: str = "TIENDA 'LA PROVIDENCIA'") -> str:
    """Genera el texto formateado de un ticket de salida / comprobante de venta."""
    lines = [
        "=" * 44,
        f"{store_name.center(44)}",
        "SISTEMA DE GESTION DE ALMACEN E INVENTARIO".center(44),
        "COMPROBANTE DE DESPACHO / VENTA".center(44),
        "=" * 44,
        f"Folio: {receipt_data.get('folio')}",
        f"Fecha: {receipt_data.get('fecha')}",
        f"Método de Pago: {receipt_data.get('metodo_pago')}",
        "-" * 44,
        f"{'CANT':<5} {'DESCRIPCIÓN':<24} {'PRECIO':>6} {'TOTAL':>7}",
        "-" * 44,
    ]

    for item in receipt_data.get("items", []):
        nombre = item["nombre"]
        if len(nombre) > 22:
            nombre = nombre[:21] + "."
        sub = item["cantidad"] * item["precio_venta"]
        lines.append(f"{item['cantidad']:<5} {nombre:<24} ${item['precio_venta']:>5.2f} ${sub:>6.2f}")

    lines.extend([
        "-" * 44,
        f"{'Subtotal:':<30} {format_currency(receipt_data.get('subtotal')):>13}",
        f"{'IVA (16%):':<30} {format_currency(receipt_data.get('iva')):>13}",
        f"{'TOTAL A PAGAR:':<30} {format_currency(receipt_data.get('total')):>13}",
        "=" * 44,
        "¡Gracias por su preferencia!".center(44),
        "Conserve este ticket para devoluciones".center(44),
        "=" * 44,
    ])
    return "\n".join(lines)
