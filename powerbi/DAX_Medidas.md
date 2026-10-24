# Medidas DAX - Etapa 4: Conocimiento evidente

Medidas creadas en el modelo de Power BI (`DinamicaEmpresarial.pbix`). Todas se calculan sobre la tabla `dataset tratado`, que corresponde a `Datos_Tratados` de la Etapa 3.

## Medidas

| Medida | Formula DAX | Descripcion |
| --- | --- | --- |
| Total Empresas | `DISTINCTCOUNT('dataset tratado'[nit])` | Numero de empresas distintas (NIT). |
| Total Insolventes | `CALCULATE(DISTINCTCOUNT('dataset tratado'[nit]), 'dataset tratado'[Insolvencia_Tecnica] = "Sí")` | Empresas con patrimonio negativo. |
| % Insolvencia | `DIVIDE([Total Insolventes], [Total Empresas], 0)` | Proporcion de empresas con insolvencia tecnica (formato porcentaje). |
| Endeudamiento Promedio | `AVERAGE('dataset tratado'[Razon_Endeudamiento])` | Promedio de la razon pasivo / activo. |
| Endeudamiento Mediano | `MEDIAN('dataset tratado'[Razon_Endeudamiento])` | Mediana de la razon pasivo / activo. |
| Endeudamiento Maximo | `MAX('dataset tratado'[Razon_Endeudamiento])` | Valor maximo de la razon pasivo / activo. |

## Codigo

```dax
Total Empresas = DISTINCTCOUNT('dataset tratado'[nit])

Total Insolventes =
CALCULATE(
    DISTINCTCOUNT('dataset tratado'[nit]),
    'dataset tratado'[Insolvencia_Tecnica] = "Sí"
)

% Insolvencia = DIVIDE([Total Insolventes], [Total Empresas], 0)

Endeudamiento Promedio = AVERAGE('dataset tratado'[Razon_Endeudamiento])

Endeudamiento Mediano = MEDIAN('dataset tratado'[Razon_Endeudamiento])

Endeudamiento Maximo = MAX('dataset tratado'[Razon_Endeudamiento])
```

## Uso por tablero

| Tablero | Pregunta | Medidas |
| --- | --- | --- |
| 1. Composicion | Como se distribuyen las empresas segun su tamano y su estado de insolvencia tecnica? | Total Empresas, Total Insolventes, % Insolvencia |
| 2. Comparacion entre grupos | Existen diferencias en el nivel de endeudamiento entre los tamanos de empresa? | Endeudamiento Promedio, Mediano y Maximo |
| 3. Comportamiento temporal | Como ha variado la insolvencia tecnica y el endeudamiento entre 2016 y 2025? | Total Empresas, % Insolvencia, Endeudamiento Mediano |
| 4. Multivariado | Que combinaciones de tamano, ano y estado de insolvencia concentran mas casos y hay perfiles inusuales? | Total Empresas, % Insolvencia, Endeudamiento Mediano |

## Segmentadores (slicers)

- `Ano_Corte` (rango 2016-2025, configurado como "No resumir").
- `Tamano_Empresa` (Micro, Pequena, Mediana, Grande, Sin clasificar).
- `Insolvencia_Tecnica` (Si, No), usado en el tablero 2.

## Modelo

- Una sola tabla de hechos: `dataset tratado` (12 columnas, 25.163 filas cargadas).
- Sin tablas de dimension ni relaciones adicionales.
- Unidad de analisis: empresa-periodo (`nit` + `fecha_corte`).
- Las medidas cuentan NIT distintos; un mismo NIT puede aparecer en varios tamanos o anos.
- La razon de endeudamiento solo existe cuando hay activo y pasivo (cerca del 3,5 % de los registros).
