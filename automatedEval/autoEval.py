import os
import pandas as pd
import openai
import pdfplumber
import docx
import Cocoa
import logging
from dotenv import load_dotenv

# ------------------------------
# CONFIGURACIÓN DE OPENAI
# ------------------------------

load_dotenv()
api_key = os.getenv("MI_CLAVE_API_OPENAI")
openai.api_key = api_key

# ------------------------------
# SELECCIÓN NATIVA DE ARCHIVO
# ------------------------------

def seleccionar_archivo(allowed_types, titulo="Selecciona un archivo"):
    panel = Cocoa.NSOpenPanel.openPanel()
    
    panel.setCanChooseFiles_(True)
    panel.setCanChooseDirectories_(False)
    panel.setAllowsMultipleSelection_(False)
    panel.setAllowedFileTypes_(allowed_types)
    panel.setTitle_(titulo)

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
            with open(path, 'r', encoding='utf-8-sig') as f:
                first_line = f.readline()
                delimiter = ";" if ";" in first_line else ","

            df = pd.read_csv(path, encoding='utf-8-sig', delimiter=delimiter)
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(path)
        else:
            raise ValueError("Formato no soportado.")
        
        print("\n✅ Rúbrica cargada correctamente:")
        print(df.head())
        return df

    except Exception as e:
        print(f"❌ Error cargando rúbrica: {e}")
        return None

# ------------------------------
# LECTURA DEL TFM (PDF / DOCX)
# ------------------------------

def leer_tfm(path):
    ext = os.path.splitext(path)[-1].lower()
    texto = ""
    
    if ext == ".pdf":
        print("📥 Leyendo PDF...")

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
# EVALUACIÓN CON OPENAI
# ------------------------------

def evaluar_criterio(criterio, descripcion_tfm):
    prompt = f"""Eres un evaluador académico experto siguiendo los criterios de UNIR. Evalúa el siguiente trabajo según el criterio:

Criterio:
{criterio}

Trabajo del TFM:
{descripcion_tfm}

Responde estrictamente con Nivel 1, Nivel 2, Nivel 3 o Nivel 4 seguido de una justificación crítica y detallada.

Ejemplo:
Nivel 3: La respuesta presenta adecuación parcial...
"""
client=openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    
    return response.choices[0].message.content

# ------------------------------
# GENERAR INFORME MARKDOWN
# ------------------------------

def generar_markdown(resultados, nombre_archivo):
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write("# Informe de Evaluación TFM\n\n")
        for res in resultados:
            f.write(f"## Criterio: {res['criterio']}\n")
            f.write(f"**Evaluación:** {res['evaluacion']}\n\n")
    print(f"✅ Informe Markdown generado: {nombre_archivo}")

# ------------------------------
# FLUJO PRINCIPAL
# ------------------------------

# Seleccionar rúbrica
archivo_rubrica = seleccionar_archivo(["xlsx", "xls", "csv"], "Selecciona la rúbrica")
if not archivo_rubrica:
    print("❗ No se seleccionó la rúbrica.")
    exit()

rubrica = cargar_rubrica(archivo_rubrica)

# Seleccionar TFM
archivo_tfm = seleccionar_archivo(["pdf", "docx"], "Selecciona el TFM (PDF o DOCX)")
if not archivo_tfm:
    print("❗ No se seleccionó el TFM.")
    exit()

texto_tfm = leer_tfm(archivo_tfm)

# Evaluar
resultados = []
for criterio in rubrica.iloc[:, 0]:
    print(f"\n🧠 Evaluando criterio: {criterio}")
    resultado = evaluar_criterio(criterio, texto_tfm)
    resultados.append({"criterio": criterio, "evaluacion": resultado})

# Guardar CSV
df_resultados = pd.DataFrame(resultados)
df_resultados.to_csv("evaluacion_tfm_resultado.csv", index=False)
print("\n✅ Resultados guardados en CSV: evaluacion_tfm_resultado.csv")

# Guardar Markdown
generar_markdown(resultados, "evaluacion_tfm_informe.md")
print("✅ Informe Markdown guardado: evaluacion_tfm_informe.md")
# Guardar JSON
df_resultados.to_json("evaluacion_tfm_resultado.json", orient="records", lines=True)
print("✅ Resultados guardados en JSON: evaluacion_tfm_resultado.json")
# Guardar TXT
with open("evaluacion_tfm_resultado.txt", "w", encoding="utf-8") as f:
    for res in resultados:
        f.write(f"Criterio: {res['criterio']}\n")
        f.write(f"Evaluación: {res['evaluacion']}\n\n")
print("✅ Resultados guardados en TXT: evaluacion_tfm_resultado.txt")