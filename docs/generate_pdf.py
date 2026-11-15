"""
generate_pdf.py - Script automatizado para compilar el documento del Proyecto Final a PDF
Utiliza el motor de renderizado de Google Chrome o Microsoft Edge en modo headless.

Uso:
    python generate_pdf.py
"""

import os
import subprocess
import shutil

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(DOCS_DIR, "ProyectoFinal_Documento.html")
PDF_PATH = os.path.join(DOCS_DIR, "ProyectoFinal_ApellidoNombre.pdf")
ROOT_PDF_PATH = os.path.join(os.path.dirname(DOCS_DIR), "ProyectoFinal_ApellidoNombre.pdf")
TEMP_PROFILE = os.path.join(DOCS_DIR, "_temp_profile")

# Posibles ejecutables de navegadores en Windows
BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
]

def find_browser():
    for path in BROWSERS:
        if os.path.exists(path):
            return path
    # Intentar comando en PATH
    for cmd in ["chrome", "msedge"]:
        path = shutil.which(cmd)
        if path:
            return path
    return None

def compile_pdf():
    browser = find_browser()
    if not browser:
        print("[ERROR] No se encontró Google Chrome ni Microsoft Edge en las rutas estándar.")
        print("        Por favor abra 'ProyectoFinal_Documento.html' en su navegador e imprima como PDF (Ctrl + P).")
        return False

    print(f"[*] Utilizando motor de renderizado: {browser}")
    print(f"[*] Compilando '{os.path.basename(HTML_PATH)}' a PDF...")

    os.makedirs(TEMP_PROFILE, exist_ok=True)
    file_url = "file:///" + HTML_PATH.replace("\\", "/")

    cmd = [
        browser,
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        f"--user-data-dir={TEMP_PROFILE}",
        f"--print-to-pdf={PDF_PATH}",
        file_url
    ]

    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
        if os.path.exists(PDF_PATH) and os.path.getsize(PDF_PATH) > 0:
            print(f"[OK] PDF generado exitosamente: {PDF_PATH} ({os.path.getsize(PDF_PATH):,} bytes)")
            shutil.copyfile(PDF_PATH, ROOT_PDF_PATH)
            
            # También generar versión con el apellido y nombre formal del estudiante
            named_pdf_docs = os.path.join(DOCS_DIR, "ProyectoFinal_EscorciaJose.pdf")
            named_pdf_root = os.path.join(os.path.dirname(DOCS_DIR), "ProyectoFinal_EscorciaJose.pdf")
            shutil.copyfile(PDF_PATH, named_pdf_docs)
            shutil.copyfile(PDF_PATH, named_pdf_root)
            print(f"[OK] Versión personalizada generada: {named_pdf_root}")
            return True
        else:
            print(f"[ERROR] No se pudo generar el archivo PDF. Salida: {res.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Excepción durante la compilación: {e}")
        return False
    finally:
        shutil.rmtree(TEMP_PROFILE, ignore_errors=True)

if __name__ == "__main__":
    compile_pdf()
