from flask import Flask, Response, render_template, send_from_directory
from data_quality import build_report, treated_csv

app = Flask(__name__)

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



if __name__ == '__main__':
    app.run(debug=True)
