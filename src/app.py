from flask import Flask
from src.models import Base, engine
from src.models.products import Products
from src.models.users import Users 
from src.models.clientes import clientes
from src.models.categoris import Categoris
from src.routes import register_routes


app = Flask(__name__)
register_routes(app)
Base.metadata.create_all(engine)


@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(debug=True)
