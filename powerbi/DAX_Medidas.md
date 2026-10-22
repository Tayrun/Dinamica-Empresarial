# Medidas DAX Principales — Etapa 4: Conocimiento Evidente

> Documentar aquí cada medida DAX creada en el modelo de Power BI.

---

## 1. Indicadores de Composición (Pregunta 1)
| Nombre | Fórmula DAX | Descripción |
|--------|-------------|-------------|
| `Total Empresas` | `DISTINCTCOUNT(Datos[nit])` | Empresas únicas en el periodo |
| `Pct Por Tamano` | `DIVIDE([Conteo Tamano], [Total Empresas])` | Participación % por categoría de tamaño |
| `Pct Insolvencia` | `DIVIDE([Conteo Insolvencia], [Total Empresas])` | Participación % por insolvencia técnica |

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
| `Var Anual Activos` | `VAR Curr = CALCULATE(SUM(Datos[Activo_Total]), Datos[Ano_Corte] = MAX(Datos[Ano_Corte])) VAR Prev = CALCULATE(SUM(Datos[Activo_Total]), Datos[Ano_Corte] = MAX(Datos[Ano_Corte]) - 1) RETURN DIVIDE(Curr - Prev, Prev)` | Variación % YoY |
| `Maximo Periodo` | `MAXX(VALUES(Datos[Ano_Corte]), CALCULATE(SUM(Datos[Activo_Total])))` | Año con mayor total de activos |
| `Minimo Periodo` | `MINX(VALUES(Datos[Ano_Corte]), CALCULATE(SUM(Datos[Activo_Total])))` | Año con menor total de activos |

---

## 4. Indicadores Multivariados (Pregunta 4)
| Nombre | Fórmula DAX | Descripción |
|--------|-------------|-------------|
| `Conteo Perfil` | `COUNTROWS(SUMMARIZE(Datos, Datos[Tamano_Empresa], Datos[Insolvencia_Tecnica], Datos[Ano_Corte]))` | Combinaciones únicas tamaño × insolvencia × año |
| `Endeudamiento Promedio Perfil` | `AVERAGEX(SUMMARIZE(Datos, Datos[Tamano_Empresa], Datos[Insolvencia_Tecnica], Datos[Ano_Corte]), CALCULATE(AVERAGE(Datos[Razon_Endeudamiento])))` | Endeudamiento medio por perfil |
| `Outlier Score` | `IF([Endeudamiento Promedio Perfil] > 2 * CALCULATE(AVERAGE(Datos[Razon_Endeudamiento]), ALL(Datos)), 1, 0)` | Flag de perfil inusual |

---

## Segmentadores (Slicers) usados
- `Tamano_Empresa` (Micro, Pequeña, Mediana, Grande)
- `Insolvencia_Tecnica` (Sí, No)
- `Ano_Corte` (2016–2025)
- `Pais_Matriz` (COL)

---

## Relaciones del modelo
- Tabla de hechos: `Datos` (dataset tratado Etapa 3)
- Sin tablas de dimensión adicionales (star schema plano)
- Clave primaria compuesta: `nit` + `fecha_corte`

---

*Actualizar este archivo cada vez que se agregue o modifique una medida DAX.*