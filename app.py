from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    metricas = {
        "tasa_supervivencia_5_anios": "45%",
        "factores_clave": [
            "Gestión del flujo de caja y liquidez",
            "Capacidad de adaptación e innovación",
            "Diversificación de clientes",
            "Eficiencia operativa y digitalización"
        ]
    }
    return render_template('index.html', data=metricas)

if __name__ == '__main__':
    app.run(debug=True)