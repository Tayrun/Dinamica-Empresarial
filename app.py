from flask import Flask, Response, render_template, send_from_directory
from data_quality import build_report, treated_csv
from os import environ
from pathlib import Path
from urllib.parse import urlparse

app = Flask(__name__)

# Enlace actual del informe del equipo. Puede sustituirse sin cambiar código
# mediante POWERBI_EMBED_URL y POWERBI_REPORT_URL en el entorno de despliegue.
POWERBI_DEFAULT_REPORT_URL = (
    "https://app.powerbi.com/view?r=eyJrIjoiZDNjMjczZjQtY2M1OC00MWU0LTlkMjgt"
    "ZWIxZGFhZjdiYzEyIiwidCI6IjA3ZGE2N2EwLTFmNDMtNGU4Yy05NzdmLTVmODhiNjQ3"
    "MGVlNiIsImMiOjR9"
)
PBIX_NAME = "DinamicaEmpresarial.pbix"

def powerbi_url(setting_name):
    """Returns only a valid HTTPS Power BI URL configured in the environment."""
    url = environ.get(setting_name, "").strip()
    parsed = urlparse(url)
    if parsed.scheme == "https" and parsed.netloc == "app.powerbi.com":
        return url
    return ""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/etapa1/1-problema-contexto')
def etapa1_problema():
    return render_template('etapa1/1_problema.html')

@app.route('/etapa1/2-preguntas-investigacion')
def etapa1_preguntas():
    return render_template('etapa1/2_preguntas.html')

@app.route('/etapa1/3-necesidades-informacion')
def etapa1_necesidades():
    return render_template('etapa1/3_necesidades.html')

@app.route('/etapa1/4-fuentes-datos')
def etapa1_fuentes():
    return render_template('etapa1/4_fuentes.html')

@app.route('/etapa1/5-dataset')
def etapa1_dataset():
    return render_template('etapa1/5_dataset.html')
#AGREGAR DATASET/DESCARGAR
@app.route('/descargas/dataset-r1')
def descargar_dataset():
    return send_from_directory('data/processed', 'dataset_consolidado_r1.csv', as_attachment=True)

@app.route('/etapa1/6-diccionario-datos')
def etapa1_diccionario():
    return render_template('etapa1/6_diccionario.html')

@app.route('/etapa1/7-calidad-inicial')
def etapa1_calidad():
    return render_template('etapa1/7_calidad.html')

@app.route('/etapa1/8-limitaciones-consideraciones')
def etapa1_limitaciones():
    return render_template('etapa1/8_limitaciones.html')

@app.route('/etapa2/calidad-datos')
def calidad_datos():
    return render_template('calidad_datos.html', report=build_report())

@app.route('/descargas/dataset-tratado')
def descargar_dataset_tratado():
    return Response(
        treated_csv(), mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename=dataset_consolidado_tratado.csv'},
    )

# --- RUTAS ETAPA 2 ---
@app.route('/etapa2/limpieza')
def etapa2_limpieza():
    return render_template('etapa2/1_limpieza.html', report=build_report())

@app.route('/etapa2/transformacion')
def etapa2_transformacion():
    return render_template('etapa2/2_transformacion.html', report=build_report())

# --- RUTAS ETAPA 3 ---
@app.route('/etapa3/resultados')
def etapa3_resultados():
    return render_template('etapa3/resultados.html')

@app.route('/descargas/informe-etapa3')
def descargar_informe_etapa3():
    return send_from_directory('data/informes', 'informe_tecnico_etapa3.pdf', as_attachment=True)

# --- RUTAS ETAPA 4 ---
@app.route('/etapa4/conocimiento-evidente')
def etapa4_conocimiento():
    pbix_path = Path(__file__).parent / PBIX_NAME
    pbix_exists = pbix_path.exists() and pbix_path.stat().st_size > 0
    
    # En local use .env o variables del sistema; en Render configúralas como variables de entorno.
    # POWERBI_EMBED_URL debe ser una URL HTTPS de app.powerbi.com apta para iframe.
    powerbi_embed_url = powerbi_url("POWERBI_EMBED_URL") or POWERBI_DEFAULT_REPORT_URL
    powerbi_report_url = powerbi_url("POWERBI_REPORT_URL") or powerbi_embed_url
    
    return render_template('etapa4/conocimiento.html', 
                           powerbi_embed_url=powerbi_embed_url,
                           powerbi_report_url=powerbi_report_url,
                           pbix_exists=pbix_exists)

@app.route('/descargas/pbix')
def descargar_pbix():
    pbix_path = Path(__file__).parent / PBIX_NAME
    if pbix_path.exists():
        return send_from_directory(Path(__file__).parent, PBIX_NAME, as_attachment=True)
    return "Archivo PBIX no encontrado.", 404

@app.route('/descargas/dax-medidas')
def descargar_dax_md():
    return send_from_directory('powerbi', 'DAX_Medidas.md', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
