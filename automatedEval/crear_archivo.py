import os
import shutil
import traceback
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from AppKit import NSOpenPanel

RUTA_LOG = os.path.expanduser("~/Desktop/traza_nativa.txt")

def trazar(mensaje):
    with open(RUTA_LOG, "a", encoding="utf-8") as f:
        f.write(mensaje + "\n")
    print("📝", mensaje)

def seleccionar_pdf():
    panel = NSOpenPanel.openPanel()
    panel.setTitle_("Selecciona un archivo PDF")
    panel.setAllowedFileTypes_(["pdf"])
    panel.setCanChooseDirectories_(False)
    panel.setAllowsMultipleSelection_(False)

    if panel.runModal() == 1:
        ruta = panel.URLs()[0].path()
        trazar(f"✅ PDF seleccionado: {ruta}")
        return ruta
    else:
        trazar("❌ No se seleccionó archivo.")
        return None

def preparar_archivo(pdf_path):
    nombre = os.path.basename(pdf_path)
    destino = os.path.join("/tmp", nombre)
    try:
        shutil.copy(pdf_path, destino)
        os.chmod(destino, 0o644)
        trazar(f"📁 Archivo copiado a ubicación segura: {destino}")
        return destino
    except Exception as e:
        trazar("❌ Error al copiar el archivo:")
        trazar(traceback.format_exc())
        return None

def asignar_valores():
    return {
        "Año académico": "2024-2025",
        "Periodo": "Primavera",
        "Tipo de estudio": "Máster",
        "Titulación": "Dirección de Procesos Estratégicos",
    }

def rellenar_desplegables(driver, valores):
    try:
        trazar("🧾 Rellenando campos desplegables...")

        campo_ano = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "IdRubricaAnoAcademico")))
        Select(campo_ano).select_by_visible_text(valores["Año académico"])
        trazar(f"✅ Año académico: {valores['Año académico']}")

        campo_periodo = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "IdRubricaPeriodo")))
        Select(campo_periodo).select_by_visible_text(valores["Periodo"])
        trazar(f"✅ Periodo: {valores['Periodo']}")

        campo_tipo = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "IdRuctTipoEstudio")))
        Select(campo_tipo).select_by_visible_text(valores["Tipo de estudio"])
        trazar(f"✅ Tipo de estudio: {valores['Tipo de estudio']}")

        campo_titulacion = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "IdRuctTitulacion")))
        Select(campo_titulacion).select_by_visible_text(valores["Titulación"])
        trazar(f"✅ Titulación: {valores['Titulación']}")

    except Exception as e:
        trazar("❌ Error al rellenar los campos desplegables.")
        trazar(traceback.format_exc())

def cargar_pdf_en_formulario(driver, pdf_path, valores):
    try:
        trazar("🌐 Accediendo a la página...")
        driver.get("https://verifirma.unir.net/Rubricas")

        # Rellenar desplegables antes de subir el archivo
        rellenar_desplegables(driver, valores)

        trazar("📄 Esperando campo de tipo file...")
        campo_archivo = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )

        trazar(f"📤 Subiendo archivo desde: {pdf_path}")
        campo_archivo.send_keys(pdf_path)
        trazar("✅ Subida enviada. Esperando transición...")

        time.sleep(3)
        url_actual = driver.current_url
        trazar(f"🌐 URL tras subida: {url_actual}")

        captura_path = os.path.expanduser("~/Desktop/captura_post_upload.png")
        driver.save_screenshot(captura_path)
        trazar(f"📸 Captura tras subida guardada: {captura_path}")

        trazar("✅ Proceso completado. Safari permanece abierto para completar el formulario manualmente.")

    except Exception as e:
        trazar("❌ Error durante la carga:")
        trazar(traceback.format_exc())
        try:
            error_capture = os.path.expanduser("~/Desktop/error_carga_nativo.png")
            driver.save_screenshot(error_capture)
            trazar(f"📸 Captura guardada en caso de error: {error_capture}")
        except:
            trazar("⚠️ No se pudo guardar la captura del error.")
        trazar("⚠️ Safari NO se cerró para inspección manual.")

def main():
    with open(RUTA_LOG, "w", encoding="utf-8") as f:
        f.write("🧪 INICIO DE TRAZA\n\n")

    trazar("🔁 Iniciando script")
    ruta_original = seleccionar_pdf()
    if not ruta_original:
        trazar("🚫 Proceso cancelado.")
        return

    ruta_local = preparar_archivo(ruta_original)
    if not ruta_local:
        trazar("🚫 No se pudo preparar el archivo local.")
        return

    try:
        trazar("🚀 Iniciando SafariDriver...")
        driver = webdriver.Safari()
        trazar("✅ Safari iniciado.")
    except Exception as e:
        trazar("❌ Error al iniciar SafariDriver.")
        trazar(traceback.format_exc())
        return

    valores = asignar_valores()
    cargar_pdf_en_formulario(driver, ruta_local, valores)

if __name__ == "__main__":
    main()
