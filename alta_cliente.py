import subprocess
import os

print("=== Alta automática de cliente SalesMind ===")
nombre = input("Nombre del cliente: ")
telegram_id = input("Telegram chat ID: ")
ruta_pdfs = input("Ruta a la carpeta de PDFs: ")

# Validar existencia de la carpeta de PDFs
def validar_carpeta(ruta):
    if not os.path.isdir(ruta):
        print(f"ERROR: La carpeta '{ruta}' no existe. Por favor, créala y coloca los PDFs antes de continuar.")
        exit(1)

validar_carpeta(ruta_pdfs)

cmd = [
    "C:/xampp/htdocs/SalesMind-agente-web/venv/Scripts/python.exe",
    "-m", "flask", "add-client",
    nombre, telegram_id, ruta_pdfs
]

print("Ejecutando alta de cliente...")
subprocess.run(cmd)
print("Listo. El cliente ha sido dado de alta si no hubo errores.")
