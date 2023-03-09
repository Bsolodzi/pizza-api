from flask_restx import Namespace, Resource, fields
from flask import request
from ..models.users import User
from ..utils import db
from werkzeug.security import generate_password_hash, check_password_hash
from http import HTTPStatus
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

auth_namespace = Namespace('auth', description= 'name space for authentication')

#serializng data in place of using schema {db to serialize, data}
signup_model = auth_namespace.model(
    'SignUp', {
        'id': fields.Integer(),
        'username': fields.String(required=True, description= 'A userame'),
        'email': fields.String(required=True, description= 'An email'),
        'password': fields.String(required=True, description= 'A password')
    }
)

user_model = auth_namespace.model(
    'User', {
        'id': fields.Integer(),
        'username': fields.String(required=True, description= 'A userame'),
        'email': fields.String(required=True, description= 'An email'),
        'password_hash': fields.String(required=True, description= 'A password'),
        'is_active': fields.Boolean(description= "This shows that User is active or not"),
        'is_staff': fields.Boolean(description= "This shows that User is a staff or not")
    }
)

login_model = auth_namespace.model(
    'Login', {
        'email': fields.String(required=True, description= 'An email'),
        'password': fields.String(required=True, description= 'A password')
    }
)

@auth_namespace.route('/signup')
class SignUp(Resource):

    @auth_namespace.expect(signup_model)
    # marshall_with converts objects to a json/dic format else your return statements wont return anything
    # marshall_with is returning user_model schema so we can return the password hash
    @auth_namespace.marshal_with(user_model)
    def post(self):
        """
            Sign up a user
        """
        data = request.get_json()

        # not including the default values
        # new_user is an object
        new_user = User(
            username = data.get('username'),
            email = data.get('email'),
            password_hash = generate_password_hash(data.get('password')) 
        )

        # saves new_user to db
        new_user.save()

        return new_user, HTTPStatus.CREATED


@auth_namespace.route('/login')
class Login(Resource):
    # @auth_namespace.marshal_with(login_model)
    @auth_namespace.expect(login_model)
    def post(self):
        """
            Generate JWT Token
        """
        #data returns a dictionary with data according to the login schema/model
        data = request.get_json()

        # data = {"email":"email", "password": "password"}

        email = data.get('email')
        password = data.get('password')

        # using the email entered, query the db and grab all details associatede with that user
        user = User.query.filter_by(email=email).first()

        #if the user is not empty, unhash password = password
        if (user is not None) and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=  user.username)
            refresh_token = create_refresh_token(identity = user.username)

            response = {
                'access_token': access_token, 
                'refresh_token': refresh_token
            }

            return response, HTTPStatus.CREATED
        
         
@auth_namespace.route('/refresh')
class Refresh(Resource):
    # user has to be loggind in to access this route
    @jwt_required(refresh=True)
    def post(self):

        # get_jwt_identity helps get the identity of the user
        username = get_jwt_identity()

        access_token = create_access_token(identity= username)

        return {'access_token': access_token}, HTTPStatus.OK
    
==