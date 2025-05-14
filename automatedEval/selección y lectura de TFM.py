import os
import pdfplumber
import docx
import Cocoa
import logging

# ------------------------------
# SELECCIÓN NATIVA DE ARCHIVO (TFM)
# ------------------------------

def seleccionar_archivo_tfm():
    panel = Cocoa.NSOpenPanel.openPanel()
    
    panel.setCanChooseFiles_(True)
    panel.setCanChooseDirectories_(False)
    panel.setAllowsMultipleSelection_(False)
    panel.setAllowedFileTypes_(["pdf", "docx"])

    if panel.runModal() == Cocoa.NSModalResponseOK:
        return panel.URLs()[0].path()
    return None

# ------------------------------
# LECTURA DEL TFM (PDF / DOCX) - VERSIÓN LIMPIA
# ------------------------------

def leer_tfm(path):
    ext = os.path.splitext(path)[-1].lower()
    texto = ""
    
    if ext == ".pdf":
        print("📥 Leyendo PDF...")

        # Silenciar los logs de pdfminer (usado internamente por pdfplumber)
        logging.getLogger("pdfminer").setLevel(logging.ERROR)

        with pdfplumber.open(path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    texto += f"\n--- Página {page_num + 1} ---\n"
                    texto += page_text + "\n"

    elif ext == ".docx":
        print("📥 Leyendo DOCX...")
        doc = docx.Document(path)
        for para in doc.paragraphs:
            texto += para.text + "\n"

    else:
        raise ValueError("Formato no soportado (solo PDF o DOCX).")
    
    return texto

# ------------------------------
# FLUJO PRINCIPAL DE PRUEBA
# ------------------------------

archivo_tfm = seleccionar_archivo_tfm()

if archivo_tfm:
    print(f"\n📂 Archivo de TFM seleccionado: {archivo_tfm}")

    texto_tfm = leer_tfm(archivo_tfm)

    print("\n✅ Contenido del TFM (primeros 1000 caracteres):\n")
    print(texto_tfm[:1000])
    
    print("\n✅ Lectura completada sin errores visibles.")
else:
    print("❗ No se seleccionó ningún archivo de TFM.")
