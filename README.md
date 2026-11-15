# Dinamica Empresarial

Aplicacion Flask para documentar el analisis de dinamica financiera e insolvencia tecnica de empresas colombianas. El proyecto incorpora la definicion del problema, preguntas de investigacion, necesidades de informacion y diccionario de datos de la Etapa 1; el perfilamiento, diagnostico y tratamiento conservador de calidad de datos de la Etapa 2; el tratamiento ETL con SSIS de la Etapa 3; el analisis exploratorio con Power BI de la Etapa 4; el analisis multidimensional sobre un modelo estrella de la Etapa 5; y el conocimiento oculto con modelos supervisados, agrupamiento y mineria de texto de la Etapa 6.

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
| 1 | ¿Cambió el porcentaje de empresas con patrimonio negativo entre periodos equivalentes y entre segmentos de tamaño? | Tiempo × Tamaño | Filtros de periodo y segmento; drill-down y roll-up por tiempo (año, bloque, periodo) y tamaño (tamaño, segmento); slice y dice al combinar filtros; pivot de la matriz. |
| 2 | ¿En qué bandas de endeudamiento se concentra cada tamaño de empresa y cuánta información falta para saberlo? | Tamaño × Condición financiera | Filtros de periodo y estado del patrimonio; nivel de tamaño, medida de la matriz (registros o porcentaje por fila) y pivot. |
| 3 | ¿Las empresas que aparecen más años se diferencian en solvencia y tamaño de las que aparecen un solo año? | Empresa × Condición financiera | Filtros de cohorte de ingreso, periodo y segmento; nivel de años observados, medida (registros o porcentaje por fila) y pivot. |
| 4 | ¿Cuántas empresas de cada año de ingreso reaparecen en los años siguientes? | Empresa (cohorte) × Tiempo | Filtros de segmento y estado; niveles de tiempo y cohorte, medida (empresas o % de reaparición) y pivot. |

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

## Etapa 6: Conocimiento Oculto

La Etapa 6 busca conocimiento que no se ve a simple vista combinando tres técnicas de minería de datos con **Orange Data Mining**: modelos supervisados, agrupamiento sin variable objetivo y minería de texto de comentarios públicos de YouTube. Los resultados se presentan en la aplicación junto con el informe técnico y el video de sustentación.

### Rutas

| Ruta | Contenido |
| --- | --- |
| `/etapa6/conocimiento-oculto` | Informe descargable, video de sustentación y resultados de los tres análisis con sus conclusiones. |
| `/descargas/informe-etapa6` | Descarga del informe técnico en PDF (`data/informes/informe_tecnico_etapa6.pdf`). |

### 1. Modelos supervisados

La variable objetivo es **endeudamiento alto** (razón Pasivo/Activo mayor que 0,60) sobre 875 empresas, con 38,2 % en la clase «Alto». Los predictores son año, tamaño y activo total; pasivo, patrimonio y razón se excluyeron para evitar fuga de información. Se evaluaron cuatro modelos con validación cruzada de 10 pliegues estratificada.

| Modelo | AUC | Exactitud | F1 | Precisión | Recall | MCC |
| --- | --- | --- | --- | --- | --- | --- |
| Logistic Regression | 0,468 | 0,618 | 0,000 | 0,000 | 0,000 | 0,000 |
| Tree | 0,530 | 0,605 | 0,117 | 0,397 | 0,069 | 0,008 |
| kNN (elegido) | 0,543 | 0,578 | 0,376 | 0,432 | 0,332 | 0,067 |
| Constant (línea base) | 0,500 | 0,618 | 0,000 | 0,000 | 0,000 | 0,000 |

kNN es el único que detecta algunos casos de endeudamiento alto, pero su AUC está casi en el azar y su exactitud queda por debajo de la línea base: **ningún modelo sirve para predecir** con estas variables.

### 2. Agrupamiento

Se aplicó k-Means con tres variables normalizadas (años observados, primer año observado y logaritmo del activo) sobre 9.163 empresas. La silueta para k = 2 a 8 va de 0,318 a 0,369; se eligió k = 4 (0,341) por interpretabilidad, aunque la estructura es débil.

| Grupo | Empresas | Años obs. (media) | Primer año (mediana) | Tamaño más frecuente | Razón de endeudamiento (mediana) |
| --- | --- | --- | --- | --- | --- |
| C1 Entrantes recientes, activo pequeño | 3.426 | 1,19 | 2020 | Pequeña | 0,503 |
| C2 Permanentes de larga trayectoria | 1.189 | 3,15 | 2016 | Mediana | 0,470 |
| C3 Cohorte 2016, pocos años | 2.728 | 1,54 | 2016 | Mediana | 0,494 |
| C4 Empresas grandes | 1.820 | 1,60 | 2018 | Grande | 0,509 |

Los grupos se separan por trayectoria y tamaño, pero el endeudamiento es casi igual en los cuatro (mediana entre 0,47 y 0,51): tampoco aquí el tamaño explica la deuda. La razón solo se conoce en 875 de las 9.163 empresas.

### 3. Minería de texto

Se usó la API oficial de YouTube para extraer comentarios de 8 videos: 1.433 comentarios principales, de los cuales quedaron **652** tras eliminar duplicados, vacíos, publicidad, comentarios demasiado cortos, sobre el formato del video y sin vocabulario económico. No se guardan nombres ni identificadores de los autores.

Flujo en Orange: **Corpus → Preprocess Text → Topic Modelling (LDA, 5 temas, coherencia 0,395) → Data Table y Group by por video.**

| Tema | Palabras clave | Lectura |
| --- | --- | --- |
| 1 | crisis, trabajo, ejemplo, empresario, gente, dinero | Experiencia y consejos de empresarios |
| 2 | impuestos, negocios, gobierno, quiebra, precios | Impuestos, precios y quiebra |
| 3 | país, gobierno, renta, corrupción, gasto | Política fiscal y gobierno |
| 4 | plata, negocio, rentable, renta, casas, rentas | Rentabilidad y negocios de renta |
| 5 | dinero, vender, negocio, trabajo, quiebra, empleo | Vender, sostener el negocio y el empleo |

Los comentarios **no representan a toda la población**: son opiniones de quienes comentan 8 videos concretos.

### 4. Conclusiones

- **Evidencia:** el endeudamiento alto no se anticipa con tamaño, año y activo (mejor AUC 0,543); los grupos por trayectoria y tamaño tienen un endeudamiento casi igual; los comentarios giran alrededor de impuestos, gobierno, precios, rentabilidad, arriendos y empleo.
- **Hipótesis:** los impuestos y los arriendos aparecen como razones de cierre en los comentarios, pero el modelo no tiene variables para comprobarlo; el endeudamiento probablemente depende de la composición del pasivo y del sector, que la muestra no trae.
- **Siguiente paso:** conseguir pasivo, sector y ubicación, ampliar la muestra de comentarios y validar los temas con lectura manual.

### Video de sustentación

El video se incrusta en la página de la Etapa 6 desde `https://youtu.be/BsIGlOk2bkY`. La URL se puede cambiar sin tocar el código con la variable de entorno `VIDEO_ETAPA6_URL`; solo se aceptan enlaces de YouTube.

### Archivos de la Etapa 6

- Plantilla: `templates/etapa6/conocimiento.html`.
- Informe técnico: `data/informes/informe_tecnico_etapa6.pdf`.
- Rutas y validación del video: `app.py`.
- Variable documentada en `.env.example`: `VIDEO_ETAPA6_URL`.

Los análisis se hicieron en Orange Data Mining y sus resultados quedaron consolidados en la página; la aplicación no requiere dependencias nuevas de Python.

## Estructura

```text
app.py                 Aplicacion y rutas Flask (Etapa 1 a Etapa 6)
data_quality.py        Perfilamiento, metricas y tratamiento reproducible
multidim.py            Consultas, indicadores y graficas del modelo estrella (Etapa 5)
vistas_multidim.py     Definicion de las cuatro vistas multidimensionales
data/processed/        Dataset consolidado
data/informes/         Informes tecnicos de las etapas 3 y 6 en PDF
data/dw.sqlite         Modelo estrella de la Etapa 5 (copia de solo lectura)
templates/             Vistas HTML de las etapas del proyecto
  etapa1/              Plantillas de la Etapa 1 (8 secciones)
  etapa2/              Plantillas de la Etapa 2 (3 secciones)
  etapa3/              Plantilla de la Etapa 3 (resultados del ETL)
  etapa4/              Plantilla de la Etapa 4 (conocimiento evidente)
  etapa5/              Plantillas de la Etapa 5 (inicio y cuatro vistas)
  etapa6/              Plantilla de la Etapa 6 (conocimiento oculto)
  scripts_sql/         Scripts SQL de tablas del ETL
powerbi/               Archivo PBIX y documentacion de medidas DAX
ETL/                   Proyecto SSIS y scripts del modelo estrella de la Etapa 5
requirements.txt       Dependencias de ejecucion
```
