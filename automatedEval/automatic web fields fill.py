import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback

RUTA_LOG = "traza_ejecucion.txt"

def trazar(mensaje):
    """Escribe un mensaje en el archivo de traza."""
    with open(RUTA_LOG, "a", encoding="utf-8") as f:
        f.write(mensaje + "\n")
    print("📝", mensaje)

def seleccionar_pdf():
    """Selecciona un archivo PDF usando AppleScript (solo en macOS)."""
    trazar("Paso 1: Ejecutando AppleScript para seleccionar PDF")
    script = '''
    set theFile to choose file with prompt "Selecciona el archivo PDF" of type {"com.adobe.pdf"}
    POSIX path of theFile
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        trazar("❌ Error o cancelación en AppleScript.")
        return None
    pdf_path = result.stdout.strip()
    trazar(f"✅ Archivo seleccionado: {pdf_path}")
    return pdf_path

def cargar_pdf_en_formulario(driver, pdf_path):
    """Carga el archivo PDF en el formulario web."""
    try:
        trazar("Paso 2: Abriendo URL del formulario...")
        driver.get("https://verifirma.unir.net/Rubricas")

        trazar("Paso 3: Esperando campo de subida...")
        campo_archivo = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )

        trazar(f"Paso 4: Subiendo archivo PDF: {pdf_path}")
        campo_archivo.send_keys(pdf_path)
        trazar("✅ Archivo cargado correctamente.")

    except Exception as e:
        trazar("❌ Error durante la carga del PDF.")
        trazar(traceback.format_exc())
        try:
            driver.save_screenshot("error_subida.png")
            trazar("📸 Captura guardada: error_subida.png")
        except:
            trazar("⚠️ No se pudo guardar la captura.")

    finally:
        driver.quit()
        trazar("🚪 Navegador cerrado.")

def main():
    with open(RUTA_LOG, "w", encoding="utf-8") as f:
        f.write("🧪 TRAZA DE EJECUCIÓN\n\n")

    trazar("🔁 Iniciando script")
    pdf_path = seleccionar_pdf()
    if not pdf_path:
        trazar("⚠️ Proceso cancelado por el usuario.")
        return

    trazar("🚀 Iniciando SafariDriver...")
    try:
        driver = webdriver.Safari()
        trazar("✅ SafariDriver iniciado.")
    except Exception as e:
        trazar("❌ Error al iniciar SafariDriver.")
        trazar(traceback.format_exc())
        return

    cargar_pdf_en_formulario(driver, pdf_path)

if __name__ == "__main__":
    main()
