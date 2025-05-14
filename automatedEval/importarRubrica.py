import os
import pandas as pd
import Cocoa

# ------------------------------
# SELECCIÓN NATIVA DE ARCHIVO (RÚBRICA)
# ------------------------------

def seleccionar_archivo_rubrica():
    panel = Cocoa.NSOpenPanel.openPanel()
    
    panel.setCanChooseFiles_(True)
    panel.setCanChooseDirectories_(False)
    panel.setAllowsMultipleSelection_(False)
    panel.setAllowedFileTypes_(["xlsx", "xls", "csv"])

    if panel.runModal() == Cocoa.NSModalResponseOK:
        return panel.URLs()[0].path()
    return None

# ------------------------------
# CARGA DE RÚBRICA
# ------------------------------

def cargar_rubrica(path):
    ext = os.path.splitext(path)[-1].lower()

    try:
        if ext == ".csv":
            rubrica = pd.read_csv(path, encoding='utf-8-sig', delimiter=";", decimal=",")
        elif ext in [".xlsx", ".xls"]:
            rubrica = pd.read_excel(path)
        else:
            raise ValueError("Formato no soportado.")
        
        print("\n✅ Rúbrica cargada correctamente:")
        print(rubrica.head())
        return rubrica
    
    except Exception as e:
        print(f"❌ Error cargando rúbrica: {e}")
        return None

# ------------------------------
# FLUJO PRINCIPAL
# ------------------------------

archivo_rubrica = seleccionar_archivo_rubrica()

if archivo_rubrica:
    print(f"\n📂 Archivo seleccionado: {archivo_rubrica}")
    rubrica = cargar_rubrica(archivo_rubrica)
else:
    print("❗ No se seleccionó ninguna rúbrica.")
