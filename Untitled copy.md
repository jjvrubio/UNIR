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