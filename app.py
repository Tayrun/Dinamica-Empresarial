from flask import Flask, render_template, send_from_directory

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

if __name__ == '__main__':
    app.run(debug=True)