# Medidas DAX Principales — Etapa 4: Conocimiento Evidente

> Documentar aquí cada medida DAX creada en el modelo de Power BI.

---

## Modelo y unidad de análisis

- Tabla principal: `Datos`, con un registro por **empresa-año** (`nit` + `fecha_corte`).
- Los porcentajes de composición se calculan sobre registros empresa-año filtrados, no sobre la suma de empresas históricas.
- No hay variable sectorial ni territorial subnacional en el dataset tratado. Las comparaciones se realizan por tamaño empresarial, insolvencia técnica y año.

## 1. Indicadores de Composición (Pregunta 1)
| Nombre | Fórmula DAX | Descripción |
|--------|-------------|-------------|
| `Registros Empresa Año` | `COUNTROWS(Datos)` | Denominador para composiciones: observaciones empresa-año bajo los filtros activos. |
| `Empresas Únicas` | `DISTINCTCOUNT(Datos[nit])` | Empresas distintas; no se suma entre años. |
| `Pct por Tamaño` | `DIVIDE([Registros Empresa Año], CALCULATE([Registros Empresa Año], ALLSELECTED(Datos[Tamano_Empresa])))` | Participación de cada tamaño sobre registros empresa-año visibles. |
| `Pct Insolvencia` | `DIVIDE([Registros Empresa Año], CALCULATE([Registros Empresa Año], ALLSELECTED(Datos[Insolvencia_Tecnica])))` | Participación de cada condición de insolvencia sobre registros visibles. |

---

## 2. Indicadores de Comparación (Pregunta 2)
| Nombre | Fórmula DAX | Descripción |
|--------|-------------|-------------|
| `Promedio Endeudamiento` | `AVERAGE(Datos[Razon_Endeudamiento])` | Razón promedio por grupo |
| `Mediana Patrimonio` | `MEDIAN(Datos[Patrimonio_Total])` | Patrimonio mediano por grupo |
| `DesvStd Activos` | `STDEV.P(Datos[Activo_Total])` | Dispersión de activos |

---

## 3. Indicadores Temporales (Pregunta 3)
| Nombre | Fórmula DAX | Descripción |
|--------|-------------|-------------|
| `Activos Totales` | `SUM(Datos[Activo_Total])` | Total de activos en miles de COP. |
| `Var Anual Activos` | `VAR AnioActual = MAX(Datos[Ano_Corte]) VAR Actual = [Activos Totales] VAR Previo = CALCULATE([Activos Totales], REMOVEFILTERS(Datos[Ano_Corte]), Datos[Ano_Corte] = AnioActual - 1) RETURN DIVIDE(Actual - Previo, Previo)` | Variación porcentual frente al año anterior comparable. |
| `Máximo Activos por Año` | `MAXX(VALUES(Datos[Ano_Corte]), CALCULATE([Activos Totales]))` | Valor máximo anual de activos; usar gráfico para identificar el año. |
| `Mínimo Activos por Año` | `MINX(VALUES(Datos[Ano_Corte]), CALCULATE([Activos Totales]))` | Valor mínimo anual de activos; usar gráfico para identificar el año. |

---

## 4. Indicadores Multivariados (Pregunta 4)
| Nombre | Fórmula DAX | Descripción |
|--------|-------------|-------------|
| `Conteo Perfil` | `COUNTROWS(SUMMARIZE(Datos, Datos[Tamano_Empresa], Datos[Insolvencia_Tecnica], Datos[Ano_Corte]))` | Combinaciones únicas tamaño × insolvencia × año |
| `Endeudamiento Promedio Perfil` | `AVERAGEX(SUMMARIZE(Datos, Datos[Tamano_Empresa], Datos[Insolvencia_Tecnica], Datos[Ano_Corte]), CALCULATE(AVERAGE(Datos[Razon_Endeudamiento])))` | Endeudamiento medio por perfil |
| `Outlier Score` | `IF([Endeudamiento Promedio Perfil] > 2 * CALCULATE(AVERAGE(Datos[Razon_Endeudamiento]), ALLSELECTED(Datos)), 1, 0)` | Indicador de perfil inusual frente al promedio visible. |

---

## Segmentadores (Slicers) usados
- `Tamano_Empresa` (Micro, Pequeña, Mediana, Grande)
- `Insolvencia_Tecnica` (Sí, No)
- `Ano_Corte` (2016–2025)
- `fecha_corte` (para filtro de fecha detallada, si se requiere)

---

## Relaciones del modelo
- Tabla de hechos: `Datos` (dataset tratado Etapa 3)
- Sin tablas de dimensión adicionales (star schema plano)
- Clave lógica compuesta: `nit` + `fecha_corte`

---

*Actualizar este archivo cada vez que se agregue o modifique una medida DAX.*
