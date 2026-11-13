USE DinamicaEmpresarial;
GO

-- 1. Vaciar el modelo (permite repetir la carga)
DELETE FROM dw.Fact_Estado_Financiero;
DELETE FROM dw.Dim_Condicion_Financiera;
DELETE FROM dw.Dim_Empresa;
DELETE FROM dw.Dim_Tamano;
DELETE FROM dw.Dim_Tiempo;
DBCC CHECKIDENT ('dw.Fact_Estado_Financiero',     RESEED, 0) WITH NO_INFOMSGS;
DBCC CHECKIDENT ('dw.Dim_Condicion_Financiera',   RESEED, 0) WITH NO_INFOMSGS;
DBCC CHECKIDENT ('dw.Dim_Empresa',                RESEED, 0) WITH NO_INFOMSGS;
DBCC CHECKIDENT ('dw.Dim_Tamano',                 RESEED, 0) WITH NO_INFOMSGS;
DBCC CHECKIDENT ('dw.Dim_Tiempo',                 RESEED, 0) WITH NO_INFOMSGS;
GO

-- 2. Dim_Tiempo: Año -> Periodo
INSERT INTO dw.Dim_Tiempo (Ano, Periodo)
SELECT DISTINCT Ano_Corte,
       CASE WHEN Ano_Corte <= 2019 THEN N'Prepandemia (2016-2019)'
            WHEN Ano_Corte <= 2021 THEN N'Pandemia (2020-2021)'
            ELSE N'Posterior (2022-2025)' END
FROM dbo.Datos_Tratados
WHERE Ano_Corte IS NOT NULL;
GO

-- 3. Dim_Tamano: Tamaño -> Segmento (incluye "Sin clasificar")
INSERT INTO dw.Dim_Tamano (Tamano, Segmento, Orden) VALUES
 (N'Micro',          N'Mipyme',         1),
 (N'Pequeña',        N'Mipyme',         2),
 (N'Mediana',        N'Mipyme',         3),
 (N'Grande',         N'Gran empresa',   4),
 (N'Sin clasificar', N'Sin clasificar', 5);
GO

-- 4. Dim_Empresa: una fila por NIT
INSERT INTO dw.Dim_Empresa (Nit, Primer_Ano_Observado, Ultimo_Ano_Observado, Anos_Observados)
SELECT nit, MIN(Ano_Corte), MAX(Ano_Corte), COUNT(DISTINCT Ano_Corte)
FROM dbo.Datos_Tratados
GROUP BY nit;
GO

-- 5. Dim_Condicion_Financiera: todas las combinaciones estado x banda
INSERT INTO dw.Dim_Condicion_Financiera (Estado_Patrimonio, Banda_Endeudamiento, Grupo_Endeudamiento)
SELECT e.Estado, b.Banda, b.Grupo
FROM (VALUES (N'Positivo'), (N'Negativo'), (N'Sin información')) AS e(Estado)
CROSS JOIN (VALUES
      (N'Baja (<=0.30)',    N'Moderado'),
      (N'Media (0.30-0.60]', N'Moderado'),
      (N'Alta (0.60-1.00]', N'Alto'),
      (N'Crítica (>1.00)',  N'Alto'),
      (N'Sin información',  N'Sin información')) AS b(Banda, Grupo);
GO

-- 6. Tabla de hechos
;WITH base AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY nit, fecha_corte
               ORDER BY (CASE WHEN Patrimonio_Total IS NULL THEN 0 ELSE 1 END
                       + CASE WHEN Activo_Total     IS NULL THEN 0 ELSE 1 END
                       + CASE WHEN Pasivo_Total     IS NULL THEN 0 ELSE 1 END) DESC,
                        Iteracion DESC) AS rn
    FROM dbo.Datos_Tratados
),
calc AS (
    SELECT b.*,
           CASE WHEN b.Patrimonio_Total IS NULL THEN N'Sin información'
                WHEN b.Patrimonio_Total < 0     THEN N'Negativo'
                ELSE N'Positivo' END AS Estado,
           CASE WHEN b.Razon_Endeudamiento IS NULL THEN N'Sin información'
                WHEN b.Razon_Endeudamiento <= 0.30 THEN N'Baja (<=0.30)'
                WHEN b.Razon_Endeudamiento <= 0.60 THEN N'Media (0.30-0.60]'
                WHEN b.Razon_Endeudamiento <= 1.00 THEN N'Alta (0.60-1.00]'
                ELSE N'Crítica (>1.00)' END AS Banda
    FROM base b
    WHERE b.rn = 1
)
INSERT INTO dw.Fact_Estado_Financiero
    (Tiempo_Key, Tamano_Key, Empresa_Key, Condicion_Key, Fecha_Corte,
     Patrimonio_Total, Activo_Total, Pasivo_Total, Razon_Endeudamiento, Insolvente)
SELECT t.Tiempo_Key, tm.Tamano_Key, e.Empresa_Key, c.Condicion_Key, k.fecha_corte,
       k.Patrimonio_Total, k.Activo_Total, k.Pasivo_Total, k.Razon_Endeudamiento,
       CASE WHEN k.Patrimonio_Total IS NULL THEN NULL
            WHEN k.Patrimonio_Total < 0     THEN 1
            ELSE 0 END
FROM calc k
JOIN      dw.Dim_Tiempo t                ON t.Ano = k.Ano_Corte
LEFT JOIN dw.Dim_Tamano tm               ON tm.Tamano = ISNULL(k.Tamano_Empresa, N'Sin clasificar')
JOIN      dw.Dim_Empresa e               ON e.Nit = k.nit
JOIN      dw.Dim_Condicion_Financiera c  ON c.Estado_Patrimonio = k.Estado
                                        AND c.Banda_Endeudamiento = k.Banda;
GO

-- 7. Comprobaciones: modelo contra datos de origen
SELECT
  (SELECT COUNT(*) FROM dbo.Datos_Tratados)                                        AS filas_origen,
  (SELECT COUNT(*) FROM dw.Fact_Estado_Financiero)                                 AS filas_hechos,
  (SELECT COUNT(DISTINCT nit) FROM dbo.Datos_Tratados)                             AS nits_origen,
  (SELECT COUNT(*) FROM dw.Dim_Empresa)                                            AS empresas_dim,
  (SELECT COUNT(*) FROM dbo.Datos_Tratados WHERE Insolvencia_Tecnica LIKE N'S%')   AS insolventes_origen,
  (SELECT SUM(CAST(Insolvente AS INT)) FROM dw.Fact_Estado_Financiero)             AS insolventes_dw,
  (SELECT SUM(Activo_Total) FROM dbo.Datos_Tratados)                               AS activo_origen,
  (SELECT SUM(Activo_Total) FROM dw.Fact_Estado_Financiero)                        AS activo_dw,
  (SELECT COUNT(*) FROM dw.Fact_Estado_Financiero
    WHERE Patrimonio_Total IS NULL AND Insolvente IS NOT NULL)                     AS incoherentes;
GO
