from flask import Flask, Response, abort, render_template, request, send_from_directory
from data_quality import build_report, treated_csv
from os import environ
from pathlib import Path
from urllib.parse import urlparse
import multidim
import vistas_multidim
import re

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

# --- RUTAS ETAPA 5: ANÁLISIS MULTIDIMENSIONAL ---
# El modelo estrella vive en data/dw.sqlite (copia del esquema dw de SQL Server).
def _abrir_modelo():
    if not multidim.DB_PATH.exists():
        abort(503, description="No se encontró data/dw.sqlite (modelo estrella de la etapa 5).")
    return multidim.connect()

@app.route('/etapa5/analisis-multidimensional')
def etapa5_inicio():
    con = _abrir_modelo()
    try:
        return render_template(
            'etapa5/inicio.html',
            resumen=vistas_multidim.resumen(con),
            conocimientos=vistas_multidim.conocimientos(con),
            ejemplos=vistas_multidim.ejemplos(con),
            validaciones=vistas_multidim.validaciones(con),
        )
    finally:
        con.close()

@app.route('/etapa5/analisis-multidimensional/vista/<int:n>')
def etapa5_vista(n):
    if n not in vistas_multidim.VISTAS:
        abort(404)
    con = _abrir_modelo()
    try:
        vista = vistas_multidim.VISTAS[n](con, request.args)
        vista['conocimientos'] = vistas_multidim.conocimientos(con)[n]
        return render_template('etapa5/vista.html', v=vista, resumen=vistas_multidim.resumen(con))
    finally:
        con.close()

# --- RUTAS ETAPA 6: CONOCIMIENTO OCULTO ---
# Enlace del video de sustentacion (maximo 10 minutos). Se puede cambiar aqui o con la
# variable de entorno VIDEO_ETAPA6_URL en Render. Solo se aceptan enlaces de YouTube.
VIDEO_ETAPA6_URL = "PENDIENTE"

def _video_youtube(url):
    """Devuelve (enlace_normal, enlace_para_incrustar) si la URL es de YouTube; si no, ('', '')."""
    url = (environ.get("VIDEO_ETAPA6_URL") or url or "").strip()
    m = re.match(r"^https://(?:www\.)?(?:youtube\.com/watch\?(?:.*&)?v=|youtu\.be/)([A-Za-z0-9_-]{11})", url)
    if not m:
        return "", ""
    vid = m.group(1)
    return "https://www.youtube.com/watch?v=" + vid, "https://www.youtube.com/embed/" + vid

@app.route('/etapa6/conocimiento-oculto')
def etapa6_conocimiento():
    video_url, video_embed = _video_youtube(VIDEO_ETAPA6_URL)
    return render_template('etapa6/conocimiento.html', video_url=video_url, video_embed=video_embed)

@app.route('/descargas/informe-etapa6')
def descargar_informe_etapa6():
    return send_from_directory('data/informes', 'informe_tecnico_etapa6.pdf', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
