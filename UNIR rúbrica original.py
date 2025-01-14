import pandas as pd
import json
import os
# Este fichero toma la rúbrica que proporcionar UNIR. Para simplificar he reducido el rango de exploración a aquellas celdas que contienen la información de la rúbrica. He eliinado las que contienen el nombre del alumno y la fecha.
# También he eliminado todas aquellas que realizan los cálculos de la nota final.
# En un asegunda etapa lo que voy a hacer es un programa que evalue el trabajo de los alumnos y eliga el nivel que debe figurar en las celdas de calificación. Para así calcular la nota final.
# Despues emplearé el  Applescript que lee la rúbrica y rellena el acta.
# Me queda por desarrollar: #
# a) un programa que usa Open Ai o Anthopic para evaluar el trabajo de los alumnos  (puedo versionear el de ESBS) y asignas la calificación correspondiente. Considerar, ToC, preguntas por capítulos y por secciones.
# b) Validación de APA 7: bibliografía y referencias. Ya está casi listo, versionear el de ESBS.
# c) Un programa que hace web scrapping para rellenar las firmas de acta y rúbrica.
# d) Un programa que lee el acta y rellena la rúbrica.

def excel_to_json_with_merged_cells(excel_file, output_file, sheet_name):
    debug_output = []

    try:
        # Leer el DataFrame completo, capturando todas las columnas inicialmente para evitar datos perdidos
        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)

        debug_output.append("DataFrame inicial:\n" + df.to_string() + "\n")
        debug_output.append(f"Forma del DataFrame inicial: {df.shape}\n")

        # Recortar el DataFrame para eliminar las primeras cuatro filas
        df = df.iloc[4:].reset_index(drop=True)

        # Limitar el DataFrame a las primeras 9 filas significativas
        df = df.iloc[:9].reset_index(drop=True)

        # Limitar el DataFrame a las columnas A a F
        df = df.iloc[:, :6]

        debug_output.append("DataFrame después de recortar las primeras cuatro filas y limitar a 9 filas y columnas A a F:\n" + df.to_string() + "\n")
        debug_output.append(f"Forma del DataFrame después de recortar las primeras cuatro filas y limitar a 9 filas y columnas A a F: {df.shape}\n")

        # Rellenar hacia adelante para abordar las repeticiones de celdas combinadas
        df = df.ffill().infer_objects(copy=False)

        debug_output.append("DataFrame después de rellenar hacia adelante:\n" + df.to_string() + "\n")
        debug_output.append(f"Forma del DataFrame después de rellenar hacia adelante: {df.shape}\n")

        # Añadir una nueva fila en el índice 0 con los encabezados y los contenidos de las celdas C4, D4, E4, F4
        new_row = ['Categoría', 'Subcategoría', 'Suspenso (0-4)', 'Aprobado (5-6)', 'Notable (7-8)', 'Sobresaliente (9-10)']
        df.loc[-1] = new_row  # Añadir la nueva fila en el índice -1
        df.index = df.index + 1  # Desplazar los índices
        df = df.sort_index()  # Ordenar el DataFrame por índice

        debug_output.append("DataFrame después de añadir la nueva fila de encabezados:\n" + df.to_string() + "\n")
        debug_output.append(f"Forma del DataFrame después de añadir la nueva fila de encabezados: {df.shape}\n")

        # Asignar encabezados para Categoría y Subcategoría desde la primera fila (índice 0 después de reiniciar)
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)

        debug_output.append("DataFrame después de asignar encabezados:\n" + df.to_string() + "\n")
        debug_output.append(f"Forma del DataFrame después de asignar encabezados: {df.shape}\n")

        # Inicializar la estructura JSON
        rubric_json = {}

        # Procesar filas y estructurar el JSON
        for index, row in df.iterrows():
            try:
                category = row.get('Categoría', None)
                subcategory = row.get('Subcategoría', None)

                debug_output.append(f"Procesando fila {index}: categoría={category}, subcategoría={subcategory}\n")

                if pd.isna(category) or pd.isna(subcategory):
                    continue

                # Eliminar caracteres de nueva línea y espacios en blanco
                category = str(category).replace('\n', ' ').strip()
                subcategory = str(subcategory).replace('\n', ' ').strip()

                if category not in rubric_json:
                    rubric_json[category] = []

                # Procesar criterios
                criteria = {
                    'Suspenso (0-4)': row['Suspenso (0-4)'],
                    'Aprobado (5-6)': row['Aprobado (5-6)'],
                    'Notable (7-8)': row['Notable (7-8)'],
                    'Sobresaliente (9-10)': row['Sobresaliente (9-10)']
                }
                rubric_json[category].append({"subcategoría": subcategory, "criterios": criteria})
            except Exception as e:
                debug_output.append(f"Error procesando fila {index}: {e}\n")
                debug_output.append(f"Datos de la fila: {row.to_dict()}\n")

        debug_output.append("Estructura JSON antes de guardar:\n" + json.dumps(rubric_json, indent=4, ensure_ascii=False) + "\n")

        # Guardar el JSON en la ruta de salida
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(rubric_json, json_file, indent=4, ensure_ascii=False)

        print(f"Archivo JSON guardado en {output_file}")

    except Exception as e:
        debug_output.append(f"Error: {e}\n")

    finally:
        # Guardar la salida de depuración en un archivo de texto
        debug_file = os.path.splitext(excel_file)[0] + "_debug.txt"
        with open(debug_file, 'w', encoding='utf-8') as debug_file:
            debug_file.write("\n".join(debug_output))

        print(f"Salida de depuración guardada en {debug_file}")

if __name__ == "__main__":
    # Ruta codificada al archivo de Excel para desarrollo y pruebas
    excel_file = "/Users/JJVR/Library/CloudStorage/OneDrive-KALEIDAGEOGRAFIAS&MERCADOSSL/UNIR/Tribunales/TFM 2024/Tribunal octubre/Día 8/Rubrica_UNIR_TFM_MAVDM.xlsx"
    
    # Especificar el nombre de la hoja de trabajo
    sheet_name = "Nombre_Alumno (1)"

    # Nombre del archivo JSON de salida
    output_file = os.path.splitext(excel_file)[0] + "_rubric.json"

    # Convertir el rango especificado a JSON
    excel_to_json_with_merged_cells(excel_file, output_file, sheet_name)
