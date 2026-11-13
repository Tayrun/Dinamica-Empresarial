USE DinamicaEmpresarial;
GO

IF SCHEMA_ID('dw') IS NULL EXEC('CREATE SCHEMA dw');
GO

-- Borrar en orden inverso a las dependencias, para poder repetir el script
DROP TABLE IF EXISTS dw.Fact_Estado_Financiero;
DROP TABLE IF EXISTS dw.Dim_Condicion_Financiera;
DROP TABLE IF EXISTS dw.Dim_Empresa;
DROP TABLE IF EXISTS dw.Dim_Tamano;
DROP TABLE IF EXISTS dw.Dim_Tiempo;
GO

-- Dimensión Tiempo: Año -> Periodo
CREATE TABLE dw.Dim_Tiempo (
    Tiempo_Key  INT IDENTITY(1,1) CONSTRAINT PK_Dim_Tiempo PRIMARY KEY,
    Ano         INT           NOT NULL CONSTRAINT UQ_Dim_Tiempo_Ano UNIQUE,
    Periodo     NVARCHAR(40)  NOT NULL
);

-- Dimensión Tamaño: Tamaño -> Segmento
CREATE TABLE dw.Dim_Tamano (
    Tamano_Key  INT IDENTITY(1,1) CONSTRAINT PK_Dim_Tamano PRIMARY KEY,
    Tamano      NVARCHAR(20)  NOT NULL CONSTRAINT UQ_Dim_Tamano UNIQUE,
    Segmento    NVARCHAR(30)  NOT NULL,
    Orden       INT           NOT NULL
);

-- Dimensión Empresa: una fila por NIT
CREATE TABLE dw.Dim_Empresa (
    Empresa_Key          INT IDENTITY(1,1) CONSTRAINT PK_Dim_Empresa PRIMARY KEY,
    Nit                  NVARCHAR(20) NOT NULL CONSTRAINT UQ_Dim_Empresa_Nit UNIQUE,
    Primer_Ano_Observado INT          NOT NULL,
    Ultimo_Ano_Observado INT          NOT NULL,
    Anos_Observados      INT          NOT NULL
);

-- Dimensión Condición Financiera: Banda -> Grupo de endeudamiento
CREATE TABLE dw.Dim_Condicion_Financiera (
    Condicion_Key        INT IDENTITY(1,1) CONSTRAINT PK_Dim_Condicion PRIMARY KEY,
    Estado_Patrimonio    NVARCHAR(20) NOT NULL,
    Banda_Endeudamiento  NVARCHAR(30) NOT NULL,
    Grupo_Endeudamiento  NVARCHAR(30) NOT NULL,
    CONSTRAINT UQ_Dim_Condicion UNIQUE (Estado_Patrimonio, Banda_Endeudamiento)
);

-- Tabla de hechos: una fila por empresa y fecha de corte
CREATE TABLE dw.Fact_Estado_Financiero (
    Hecho_Key           BIGINT IDENTITY(1,1) CONSTRAINT PK_Fact PRIMARY KEY,
    Tiempo_Key          INT  NOT NULL CONSTRAINT FK_Fact_Tiempo    REFERENCES dw.Dim_Tiempo(Tiempo_Key),
    Tamano_Key          INT  NOT NULL CONSTRAINT FK_Fact_Tamano    REFERENCES dw.Dim_Tamano(Tamano_Key),
    Empresa_Key         INT  NOT NULL CONSTRAINT FK_Fact_Empresa   REFERENCES dw.Dim_Empresa(Empresa_Key),
    Condicion_Key       INT  NOT NULL CONSTRAINT FK_Fact_Condicion REFERENCES dw.Dim_Condicion_Financiera(Condicion_Key),
    Fecha_Corte         DATE NOT NULL,
    Patrimonio_Total    FLOAT NULL,
    Activo_Total        FLOAT NULL,
    Pasivo_Total        FLOAT NULL,
    Razon_Endeudamiento FLOAT NULL,
    Insolvente          TINYINT NULL CONSTRAINT CK_Fact_Insolvente CHECK (Insolvente IN (0,1)),
    CONSTRAINT UQ_Fact_Empresa_Fecha UNIQUE (Empresa_Key, Fecha_Corte)
);
GO
