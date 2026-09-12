# Dinamica Empresarial

Aplicacion Flask para documentar el analisis de dinamica financiera e insolvencia tecnica de empresas colombianas. El proyecto incorpora el perfilamiento, diagnostico y tratamiento conservador de calidad de datos de la Etapa 2.

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

## Estructura

```text
app.py                 Aplicacion y rutas Flask
data_quality.py        Perfilamiento, metricas y tratamiento reproducible
data/processed/        Dataset consolidado
templates/             Vistas HTML de las etapas del proyecto
requirements.txt       Dependencias de ejecucion
```
