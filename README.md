# Dinamica Empresarial

Aplicacion Flask para documentar el analisis de dinamica financiera e insolvencia tecnica de empresas colombianas. El proyecto incorpora la definicion del problema, preguntas de investigacion, necesidades de informacion y diccionario de datos de la Etapa 1; el perfilamiento, diagnostico y tratamiento conservador de calidad de datos de la Etapa 2; el tratamiento ETL con SSIS de la Etapa 3; el analisis exploratorio con Power BI de la Etapa 4; y el analisis multidimensional sobre un modelo estrella de la Etapa 5.

## Requisitos

- Python 3.10 o superior
- Dependencias definidas en `requirements.txt`

## Instalacion y ejecucion local

```bash
python -m venv .venv
```

En Windows:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

La aplicacion queda disponible en `http://127.0.0.1:5000`.

## Dataset

- Fuente: Sistema de Informacion y Reporte Empresarial (SIREM), Superintendencia de Sociedades de Colombia.
- Archivo de trabajo: `data/processed/dataset_consolidado_r1.csv`.
- Unidad de analisis: empresa-periodo, identificada por `nit` y `fecha_corte`.
- Periodo: 2016 a 2025.
- Variables principales: activos, pasivos, patrimonio, tamano de empresa, razon de endeudamiento e insolvencia tecnica.

## Etapa 1: Definicion del Problema

La Etapa 1 organiza las siguientes rutas:

| Ruta | Contenido |
| --- | --- |
| `/etapa1/1-problema-contexto` | Definicion del problema y contexto del proyecto |
| `/etapa1/2-preguntas-investigacion` | Preguntas de investigacion y conocimientos esperados |
| `/etapa1/3-necesidades-informacion` | Necesidades de informacion para el analisis |
| `/etapa1/4-fuentes-datos` | Recoleccion y seleccion de fuentes de datos |
| `/etapa1/5-dataset` | Dataset inicial y descripcion de la fuente |
| `/descargas/dataset-r1` | Descarga del dataset consolidado original (r1) |
| `/etapa1/6-diccionario-datos` | Diccionario de datos y variables principales |
| `/etapa1/7-calidad-inicial` | Diagnostico de calidad inicial del dataset |
| `/etapa1/8-limitaciones-consideraciones` | Limitaciones y consideraciones del proyecto |

## Calidad de Datos

La Etapa 2 se organiza en las siguientes rutas:

| Ruta | Contenido |
| --- | --- |
| `/etapa2/calidad-datos` | Descripcion del conjunto, requisitos, perfilamiento, metricas e inventario de problemas. |
| `/etapa2/limpieza` | Plan de tratamiento y analisis de causas. |
| `/etapa2/transformacion` | Reglas de integracion, homologacion y validacion de dominios. |
| `/etapa2/eda` | Comparacion antes y despues del tratamiento. |
| `/descargas/dataset-tratado` | Descarga de una copia tratada sin modificar la fuente. |

El perfilamiento evalua completitud, exactitud, consistencia, unicidad, validez y actualidad. Los valores nulos, atipicos y diferencias contables se conservan como evidencia; la copia tratada solo normaliza espacios externos y reemplaza razones de endeudamiento infinitas por valores no calculables.

## Etapa 3: Tratamiento ETL con SSIS

La Etapa 3 implementa un proceso ETL con SQL Server Integration Services (SSIS) para tratar los problemas de calidad detectados en la Etapa 2. El paquete recibe el dataset consolidado, aplica limpieza, validacion y homologacion, y escribe el resultado en SQL Server separando los registros aceptados de los que requieren revision. Se ejecutaron tres iteraciones con trazabilidad completa y sin duplicados al reejecutar el mismo lote.

| Ruta | Contenido |
| --- | --- |
| `/etapa3/resultados` | Introduccion, tabla de las tres iteraciones, evidencia de no duplicados, boton de descarga del informe y video. |
| `/descargas/informe-etapa3` | Descarga del informe tecnico en PDF (`data/informes/informe_tecnico_etapa3.pdf`). |

Resultados de las iteraciones (25.430 registros recibidos):

| Iteracion | Ajuste aplicado | Aceptados | A revision |
| --- | --- | --- | --- |
| 1 | Limpieza basica de vacios + deteccion de infinitos | 25.428 | 2 |
| 2 | + Recalcular Tamano_Empresa + deteccion de diferencia contable | 25.164 | 266 |
| 3 | + Componente Lookup anti-duplicados | 25.164 | 266 |

Archivos del proceso ETL en el repositorio:

- Paquete SSIS: `ETL/ETL_DinamicaEmpresarial/Package.dtsx`
- Scripts SQL de tablas: `templates/scripts_sql/crear_tablas.sql`
- Informe tecnico: `data/informes/informe_tecnico_etapa3.pdf`

Enlaces:

- Aplicacion publicada: `https://dinamica-empresarial.onrender.com/`
- Seccion Etapa 3: `https://dinamica-empresarial.onrender.com/etapa3/resultados`
- Video de demostracion: `https://youtu.be/2rTh9h73rkk`

## Etapa 4: Conocimiento Evidente

La Etapa 4 realiza un analisis exploratorio (Conocimiento Evidente) sobre los datos tratados en la Etapa 3 (25.164 registros, empresa–año). Se formulan 4 preguntas de análisis y se construyen 4 tableros en Power BI con 12 indicadores, 12 visualizaciones, 12 conocimientos evidentes, 8 segmentadores, interpretaciones, limitaciones y decisiones sustentadas.

### Preguntas de análisis

| # | Pregunta | Enfoque |
|---|----------|---------|
| 1 | ¿Cómo se distribuyen los registros empresa-año por tamaño empresarial e insolvencia técnica en el periodo 2016–2025? | Composición y distribución de la población |
| 2 | ¿Existen diferencias en endeudamiento, patrimonio y activos entre empresas de distinto tamaño o condición de insolvencia? | Comparación entre grupos |
| 3 | ¿Cómo evolucionan los indicadores financieros entre 2016 y 2025? | Comportamiento temporal |
| 4 | ¿Qué perfiles emergen al cruzar tamaño, insolvencia, año y variables financieras? | Análisis multivariado (3+ variables) |

### Tableros Power BI

- **Archivo PBIX:** `powerbi/Conocimiento_Evidente.pbix` (o enlace de descarga si >100 MB)
- **Medidas DAX documentadas:** `powerbi/DAX_Medidas.md`
- **4 páginas de análisis** (una por pregunta) con: título, pregunta, variables, 3 KPIs, 3 visualizaciones, 2 segmentadores, interpretación, 3 conocimientos evidentes (8 elementos cada uno), 1 limitación, 1 decisión sustentada
- **Total:** 12 indicadores, 12 visualizaciones, 12 conocimientos evidentes, 8 segmentadores

### Acceso al informe

| Recurso | Enlace / Ubicación |
|---------|-------------------|
| Informe interactivo (embed) | Variable de entorno `POWERBI_EMBED_URL` |
| Abrir en Power BI Service | Variable de entorno opcional `POWERBI_REPORT_URL` |
| PBIX (descarga) | `powerbi/Conocimiento_Evidente.pbix` o enlace en Releases |
| Sección en la app Flask | `/etapa4/conocimiento-evidente` |
| App publicada | `https://dinamica-empresarial.onrender.com/etapa4/conocimiento-evidente` |

### Datos utilizados

- **Origen:** `data/processed/dataset_consolidado_r1.csv` (dataset crudo)
- **Tratado:** Resultado del ETL Etapa 3 (SSIS) → 25.164 registros aceptados, 266 en revisión
- **Unidad de análisis:** empresa–año (`nit` + `fecha_corte`)
- **Periodo:** 2016–2025
- **Variables clave:** `Activo_Total`, `Pasivo_Total`, `Patrimonio_Total`, `Razon_Endeudamiento`, `Tamano_Empresa`, `Insolvencia_Tecnica`, `Ano_Corte`, `Pais_Matriz`
- **Limitación:** no hay una variable sectorial ni territorial subnacional; las comparaciones se realizan por tamaño, insolvencia y tiempo.

### Configuración de Power BI

Cuando el informe esté publicado, configura estas variables en el entorno local y en Render:

```text
POWERBI_EMBED_URL=https://app.powerbi.com/view?r=...
POWERBI_REPORT_URL=https://app.powerbi.com/view?r=...
```

La aplicación solo incrusta URLs HTTPS del dominio `app.powerbi.com`. La URL de inserción se muestra dentro de la Etapa 4 y la segunda, si se configura, ofrece un acceso directo al informe.

## Etapa 5: Analisis Multidimensional

La Etapa 5 organiza los datos tratados en un **modelo estrella** (esquema `dw`) y aplica las cinco operaciones OLAP para responder preguntas desde varias perspectivas a la vez: tiempo, tamaño, empresa y condición financiera. No repite las consultas de la Etapa 4: recalcula los porcentajes con su base real (registros con patrimonio conocido), compara periodos equivalentes y permite subir y bajar por las jerarquías.

### Rutas

| Ruta | Contenido |
| --- | --- |
| `/etapa5/analisis-multidimensional` | Propósito, relación con la Etapa 4, diagrama del modelo estrella, diccionario de dimensiones y medidas, ejemplos de las cinco operaciones OLAP, los ocho conocimientos y las validaciones del modelo. |
| `/etapa5/analisis-multidimensional/vista/1` | Insolvencia patrimonial en el tiempo y por tamaño (Tiempo × Tamaño). |
| `/etapa5/analisis-multidimensional/vista/2` | Perfil de endeudamiento por tamaño (Tamaño × Condición financiera). |
| `/etapa5/analisis-multidimensional/vista/3` | Años observados y solvencia de las empresas (Empresa × Condición financiera). |
| `/etapa5/analisis-multidimensional/vista/4` | Cohortes de ingreso y reaparición de empresas (Empresa/cohorte × Tiempo). |

### Modelo estrella

El modelo se construye en SQL Server y se publica en la aplicación como una copia de solo lectura en `data/dw.sqlite`. Una fila de la tabla de hechos representa una empresa (NIT) en una fecha de corte.

| Tabla | Grano / contenido | Jerarquía |
| --- | --- | --- |
| `Fact_Estado_Financiero` | Una fila por empresa y fecha de corte; patrimonio, activo, pasivo, razón de endeudamiento e indicador `Insolvente` (0/1, vacío si no se conoce el patrimonio). | — |
| `Dim_Tiempo` | Un año por fila. | Año → Bloque de 2 años (2018–2019, 2020–2021) → Periodo (Prepandemia, Pandemia, Posterior) |
| `Dim_Tamano` | Tamaño, segmento y orden. | Micro, Pequeña, Mediana → Mipyme; Grande → Gran empresa; Sin clasificar |
| `Dim_Empresa` | Una fila por NIT con primer y último año observado y años observados. | Años observados (1, 2, 3 o más); Cohorte (primer año) → Periodo de ingreso |
| `Dim_Condicion_Financiera` | Estado del patrimonio y banda/grupo de endeudamiento. | Estado (Positivo, Negativo, Sin información); Banda → Grupo de endeudamiento |

Las bandas de endeudamiento se definen sobre la razón pasivo/activo: Baja ≤ 0,30; Media hasta 0,60; Alta hasta 1,00; Crítica > 1,00. Los registros sin razón quedan en «Sin información» y no se imputan.

### Vistas y operaciones OLAP

| Vista | Pregunta | Dimensiones | Operaciones disponibles |
| --- | --- | --- | --- |
| 1 | ¿Cambió el porcentaje de empresas con patrimonio negativo entre periodos equivalentes y entre segmentos de tamaño? | Tiempo × Tamaño | Drill-down y roll-up por tiempo (año, bloque, periodo) y tamaño (tamaño, segmento); slice y dice con filtros de periodo y segmento; pivot de la matriz. |
| 2 | ¿En qué bandas de endeudamiento se concentra cada tamaño de empresa y cuánta información falta para saberlo? | Tamaño × Condición financiera | Niveles de tamaño, medida de la matriz (registros o porcentaje por fila) y pivot. |
| 3 | ¿Las empresas que aparecen más años se diferencian en solvencia y tamaño de las que aparecen un solo año? | Empresa × Condición financiera | Filtro de cohorte de ingreso, años observados, medida y pivot. |
| 4 | ¿Cuántas empresas de cada año de ingreso reaparecen en los años siguientes? | Empresa (cohorte) × Tiempo | Filtro de cohorte, medida de reaparición, matriz cohorte × año y pivot. |

Cada vista incluye filtros, controles de nivel y medida, selección activa, indicadores, gráficas, matriz de resultados con su base (n), interpretación, dos conocimientos con evidencia y consulta SQL, limitación y decisión sustentada. En total son **ocho conocimientos** (dos por vista).

Las medidas principales son: % con patrimonio negativo (Σ insolventes / registros con patrimonio conocido), razón de endeudamiento agregada (Σ pasivos / Σ activos, no promedio de razones), % de reaparición, registros, empresas distintas y años observados.

### Validaciones del modelo

La página general compara el modelo con los datos tratados de la Etapa 3:

| Validación | Valor esperado |
| --- | --- |
| Filas de la tabla de hechos | 25.164 |
| Empresas distintas (NIT) / filas de `Dim_Empresa` | 18.652 |
| Registros con patrimonio negativo | 335 |
| Suma de `Activo_Total` | 570.991.663.932,36 |
| Combinaciones (empresa, fecha) repetidas | 0 |
| Claves foráneas sin registro relacionado | 0 |
| `Insolvente` con patrimonio vacío | 0 |

### Archivos de la Etapa 5

- Modelo publicado: `data/dw.sqlite` (copia de solo lectura; la aplicación responde `503` si no existe).
- Capa de consulta y formato: `multidim.py` (solo biblioteca estándar y `markupsafe`, sin dependencias nuevas).
- Definición de las cuatro vistas: `vistas_multidim.py`.
- Plantillas: `templates/etapa5/inicio.html` y `templates/etapa5/vista.html`.
- Creación del esquema: `ETL/Modelo_estrella.sql`.
- Carga desde `dbo.Datos_Tratados`: `ETL/Cargar_modelo_estrella.sql`.

Para ejecutar la Etapa 5 basta con las dependencias actuales de `requirements.txt`; no se requieren paquetes adicionales de análisis.

## Estructura

```text
app.py                 Aplicacion y rutas Flask (Etapa 1 a Etapa 5)
data_quality.py        Perfilamiento, metricas y tratamiento reproducible
multidim.py            Consultas, indicadores y graficas del modelo estrella (Etapa 5)
vistas_multidim.py     Definicion de las cuatro vistas multidimensionales
data/processed/        Dataset consolidado
data/informes/         Informe tecnico de la Etapa 3 en PDF
data/dw.sqlite         Modelo estrella de la Etapa 5 (copia de solo lectura)
templates/             Vistas HTML de las etapas del proyecto
  etapa1/              Plantillas de la Etapa 1 (8 secciones)
  etapa2/              Plantillas de la Etapa 2 (3 secciones)
  etapa3/              Plantilla de la Etapa 3 (resultados del ETL)
  etapa4/              Plantilla de la Etapa 4 (conocimiento evidente)
  etapa5/              Plantillas de la Etapa 5 (inicio y cuatro vistas)
  scripts_sql/         Scripts SQL de tablas del ETL
powerbi/               Archivo PBIX y documentacion de medidas DAX
ETL/                   Proyecto SSIS y scripts del modelo estrella de la Etapa 5
requirements.txt       Dependencias de ejecucion
```
