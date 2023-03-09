from flask import Flask
from flask_restx import Api
from .orders.views import order_namespace
from .auth.views import auth_namespace
#locate the config dir, config fie and import config_dict
from .config.config import config_dict
from .utils import db
from .models.orders import Order
from .models.users import User
#flask migrate helps us to modify our database without having to delete it
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
# error handling library
from werkzeug.exceptions import NotFound, MethodNotAllowed


def create_app(config=config_dict['dev']):
    app = Flask(__name__)

    app.config.from_object(config)

    #telling db, this is our app
    db.init_app(app)

    #
    jwt = JWTManager(app)
    
    #takes two 
    migrate = Migrate(app, db)

    authorizations = {
        "Bearer Auth": {
            "type" : "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Add a JWT token to the header with ** Bearer &lt: JWT&gt token to authorize ** as prefix"
        }
        
    }

    api = Api(app, 
              title = "Pizza Delivery API",
              description= "A simple pizza delivery REST API service",
              authorizations= authorizations, 
              security= "Bearer Auth"
            )

    api.add_namespace(order_namespace)
    api.add_namespace(auth_namespace, path="/auth")

    # error handling
    @api.errorhandler(NotFound)
    def not_found(error):
        return {"error": "Not Found"}, 404 
    
    @api.errorhandler(MethodNotAllowed)
    def method_not_allowed(error):
        return {"error": "Method Not Allowed"}, 404

    # adding/connecting to the shell so that we can migrate and create the db
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'user': User,
            'order': Order,
        }

    return app