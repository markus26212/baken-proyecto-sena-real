
from src.routes.v1.products_routes import products_bp
from src.routes.v1.clients_routes import clients_bp
from src.routes.v1.invoices_routes import invoices_bp
from src.routes.v1.invoice_details_routes import invoice_details_bp
from src.routes.v1.auth_routes import auth_bp
from src.routes.v1.users_routes import users_bp

def register_routes(app):
    for blueprint in (auth_bp,users_bp,products_bp,clients_bp,invoices_bp,invoice_details_bp):
        app.register_blueprint(blueprint)
