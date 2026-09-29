-- Script de creación de base de datos y tablas para el ETL de Calidad de Datos (Etapa 3)
CREATE DATABASE DinamicaEmpresarial;
GO
USE DinamicaEmpresarial;
GO

CREATE TABLE dbo.Staging_SIREM (
    nit NVARCHAR(50),
    fecha_corte NVARCHAR(50),
    Patrimonio_Total NVARCHAR(50),
    Activo_Total NVARCHAR(50),
    Pasivo_Total NVARCHAR(50),
    Tamano_Empresa NVARCHAR(50),
    Razon_Endeudamiento NVARCHAR(50),
    Insolvencia_Tecnica NVARCHAR(50),
    Ano_Corte NVARCHAR(50),
    Fuente NVARCHAR(50),
    Pais_Matriz NVARCHAR(50)
);
GO

CREATE TABLE dbo.Datos_Tratados (
    nit NVARCHAR(50),
    fecha_corte DATE,
    Patrimonio_Total FLOAT NULL,
    Activo_Total FLOAT NULL,
    Pasivo_Total FLOAT NULL,
    Tamano_Empresa NVARCHAR(20) NULL,
    Razon_Endeudamiento FLOAT NULL,
    Insolvencia_Tecnica NVARCHAR(5),
    Ano_Corte INT,
    Fuente NVARCHAR(50),
    Pais_Matriz NVARCHAR(10),
    Iteracion INT
);
GO

CREATE TABLE dbo.Registros_Revision (
    nit NVARCHAR(50),
    fecha_corte_original NVARCHAR(50),
    valor_original_json NVARCHAR(MAX),
    motivo_revision NVARCHAR(200),
    Iteracion INT
);
GO