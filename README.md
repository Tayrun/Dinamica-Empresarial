# Dinamica Empresarial

Aplicacion Flask para documentar el analisis de dinamica financiera e insolvencia tecnica de empresas colombianas. El proyecto incorpora el perfilamiento, diagnostico y tratamiento conservador de calidad de datos de la Etapa 2, ademas de la definicion del problema, preguntas de investigacion, necesidades de informacion y diccionario de datos de la Etapa 1, y el tratamiento ETL con SSIS de la Etapa 3.

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

## Estructura

```text
app.py                 Aplicacion y rutas Flask (Etapa 1, Etapa 2 y Etapa 3)
data_quality.py        Perfilamiento, metricas y tratamiento reproducible
data/processed/        Dataset consolidado
data/informes/         Informe tecnico de la Etapa 3 en PDF
templates/             Vistas HTML de las etapas del proyecto
  etapa1/              Plantillas de la Etapa 1 (8 secciones)
  etapa2/              Plantillas de la Etapa 2 (4 secciones)
  etapa3/              Plantilla de la Etapa 3 (resultados del ETL)
  scripts_sql/         Scripts SQL de tablas del ETL
ETL/                   Proyecto SSIS (paquete .dtsx y solucion)
requirements.txt       Dependencias de ejecucion
```
