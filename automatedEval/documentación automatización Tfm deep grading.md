Perfecto — ahora entramos en la **Fase de Diseño de Arquitectura del Programa**, que será el puente para transformar todo este conocimiento y proceso en un **sistema automático de evaluación por API de OpenAI**.

---

# 📌 **Arquitectura Propuesta para la Evaluación Automática de TFM**

## 1️⃣ **Flujo General del Sistema**

```
[Usuario] → [Interfaz (Web o Local)] → [Carga de TFM (.pdf)] → [Extractor de Texto] → [Generador de Prompt Maestro] → [API OpenAI (Evaluación)] → [Parser de Respuesta] → [Informe Estructurado (.md o .pdf)]
```

### Etapas detalladas:

#### 🚦 Entrada

* El usuario sube un documento en formato PDF (TFM).
* Opción de añadir observaciones adicionales (opcional).

#### 📥 Procesado de documento

* **Extractor de texto automático (PDF → Texto limpio estructurado)**.
* Pre-procesado opcional para eliminar encabezados/pies de página irrelevantes.

#### 🧠 Generación de Prompt Maestro

* Inserción automática del texto extraído dentro del Prompt Maestro estructurado.
* Personalización del prompt si el usuario marca opciones especiales (ejemplo: modalidad, país, idioma...).

#### 🤖 Evaluación (API OpenAI)

* Envío del prompt completo a la API de OpenAI.
* Recepción del texto de evaluación.

#### 📊 Parser y formateo

* Interpretación estructurada de la respuesta.
* Generación de un archivo de resultados en formato Markdown, que posteriormente puede exportarse a PDF.

#### 📤 Salida

* Archivo descargable con evaluación final, tablas resumen, niveles, áreas de mejora y preguntas críticas.

---

## 2️⃣ **Módulos Principales**

| Módulo                     | Función                                                           | Tecnología recomendada                            |
| -------------------------- | ----------------------------------------------------------------- | ------------------------------------------------- |
| Interfaz de usuario        | Subida de archivo, selección de opciones, obtención de resultados | Web (Streamlit / FastAPI + simple frontend) o CLI |
| Procesador de PDF          | Extraer texto estructurado del TFM                                | PyPDF2 / pdfminer.six                             |
| Generador de Prompt        | Construir el Prompt Maestro con el texto del TFM                  | Python (string templates)                         |
| Evaluador (API Client)     | Enviar prompt a OpenAI y recibir respuesta                        | OpenAI Python SDK                                 |
| Analizador de resultados   | Parsear respuesta y generar tabla + informe                       | Python (Markdown generator + Pandas opcional)     |
| Generador de informe final | Exportar resultados a Markdown / PDF                              | Markdown + Pandoc o similar                       |

---

## 3️⃣ **Opciones futuras (Roadmap)**

✅ **Batch evaluation** → Subir varios TFMs y evaluarlos de manera masiva.

✅ **Soporte multilingüe** → Incluir soporte automático para TFMs en español e inglés.

✅ **Interfaz web avanzada con autenticación** → Para uso por parte de directores y tutores de TFM.

✅ **Dashboard de resultados** → Histórico de evaluaciones por estudiante y generación de estadísticas.

✅ **Módulo de revisión manual asistida** → Permitir a un evaluador humano añadir ajustes sobre la respuesta del modelo.

---

## 4️⃣ **Diagrama visual**

```
[ Usuario ]
     |
     V
[ Subida PDF + opciones ] ---> [ Extracción texto ]
                                         |
                                         V
                              [ Generación Prompt ]
                                         |
                                         V
                                [ OpenAI API ]
                                         |
                                         V
                               [ Evaluación recibida ]
                                         |
                                         V
[ Informe Markdown + tabla resumen + preguntas ] ----> [ PDF descargable ]
```

---

## ✅ Conclusión

El diseño que te propongo es:

* **Minimalista pero escalable** → para empezar pronto y poder añadir más funcionalidades a futuro.
* **Compatible con la API de OpenAI de manera directa.**
* **Document-centric** → La carga principal es el análisis del TFM, no necesita otros datos iniciales.
----

Perfecto. Retomando desde el punto en que lo dejamos, y según el **Prompt Maestro para Evaluación Automatizada de TFM (UNIR)** que ya está completamente definido y estandarizado, vamos a estructurar el **programa evaluador automático**.

Como punto de partida claro, te propongo esta hoja de ruta estructurada para su desarrollo:

------

## 📌 **Fase 1 — Diseño del Programa Evaluador (Conceptual)**

### 📍 **Objetivo**

Automatizar la evaluación de Trabajos de Fin de Máster (TFM) siguiendo la rúbrica institucional de UNIR con criterios claros, objetivos y justificativos, de forma estructurada y replicable.

### 📍 **Componentes principales del sistema**

#### 1️⃣ **Entrada**

- Documento TFM completo (PDF, DOCX, etc.)
- Rúbrica de evaluación (estandarizada y precargada)

#### 2️⃣ **Procesamiento**

- Preprocesado del texto (OCR si es necesario, limpieza de texto)
- Análisis seccional (detectar Portada, Resumen, Introducción, etc.)
- Análisis de contenido (estilo, justificación, coherencia, referencias APA, etc.)
- Análisis cuantitativo (tablas, gráficos, figuras, citas)

#### 3️⃣ **Evaluación**

- Aplicación de la rúbrica por criterio:
  - Nivel alcanzado (1-4)
  - Justificación académica
  - Áreas de mejora

#### 4️⃣ **Salida**

- Informe estructurado de evaluación:
  - Evaluación detallada por criterio
  - Tabla resumen
  - Conclusión global
  - Preguntas para clarificación

------

## 📌 **Fase 2 — Especificación Técnica**

### 📍 **Librerías sugeridas**

| Objetivo                           | Librería sugerida                                            | Motivo                                                       |
| ---------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Lectura de documentos              | `PyPDF2` o `python-docx` (si es docx)                        | Muy ligeras y sin problemas en ARM                           |
| Procesado de texto                 | `re`, `string`, `difflib`, `unicodedata`                     | 100% stdlib                                                  |
| Análisis de gramática básico       | `textblob` opcional / `re` / `str`                           | `textblob` es ligero y ARM-friendly, aunque podemos prescindir |
| Estructura de datos                | `csv`, `json`, `dataclasses`                                 | stdlib                                                       |
| Generación de informes             | `json` / `markdown` / `html` (opcional jinja2 muy ligera si es necesario) | Compatible y sencillo                                        |
| Evaluación heurística              | 100% Python puro                                             | Solo lógica                                                  |
| OpenAI para evaluaciones complejas | `openai`                                                     | ARM friendly                                                 |

### 📍 **Estructura inicial del programa (módulos)**

```plaintext
tfe_evaluator/
├── rubric_loader.py         # Cargar la rúbrica CSV y preparar estructura de criterios
├── document_reader.py       # Leer PDF o DOCX y extraer texto limpio
├── section_detector.py      # Detectar secciones (regex, búsqueda simple)
├── evaluator.py             # Aplicar criterios con heurísticas básicas
├── report_generator.py      # Generar informe en texto/markdown
└── main.py                  # Ejecución y orquestación
```

------

## 📍 **Extra — Optimización para Mac ARM**

- Evitar pandas (pesado en ARM, salvo necesario)
- Evitar matplotlib salvo para gráficos finales, preferir texto/tablas simples en markdown
- Preferir `pathlib`, `csv` y `dataclasses` para manipulación de archivos y estructuras → Rápidos y nativos.



## 📌 **Fase 3 — Primer Paso de Desarrollo**

Propuesta para iniciar en la siguiente sesión:

✅ **Paso 1 — Crear el esquema de criterios y niveles en código**

- Lectura de la rúbrica desde archivo (el que has subido es ideal: `rubrica.csv`)
- Definir la estructura de datos para almacenar:
  - Criterio
  - Porcentaje
  - Niveles 1-4 (descripción)
  - Resultado de evaluación

✅ **Paso 2 — Preparar extractor inicial del TFM**

- Leer documento
- Detectar secciones básicas (Portada, Resumen, Índice...)

✅ **Paso 3 — Primer test con criterio simple**

- Probar con criterio de “Formato y lenguaje”:
  - Analizar si hay errores ortográficos o formato no uniforme
  - Dar puntuación automática basada en heurística
