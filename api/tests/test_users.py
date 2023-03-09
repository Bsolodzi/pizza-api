# unittest is in-built for python testing, no need to install
import unittest
# create_up is used to configure our app, whether dev, prod or testing
from .. import create_app
from ..config.config import config_dict
from ..utils import db 
from werkzeug.security import generate_password_hash
from ..models.users import User


class UserTestCase(unittest.TestCase):
    # 
    def setUp (self):
        # telling the config we're using the testing dict 
        self.app = create_app(config=config_dict['test'])

        # app context help run the db in shell, similar to creating a shell context
        self.appctx = self.app.app_context()

        # push =create/add, pop = delete
        self.appctx.push()

        # client is coming from our app
        self.client = self.app.test_client()

        db.create_all()
    
    # tear down function is what we want to achieve
    # more like resettnig the app
    # teardown needs to come after the set up else, the tables would still be available
    def tearDown(self):
        # drops all tables if there are existing ones
        db.drop_all()

        self.appctx.pop()

        self.app = None

        self.client = None

    def test_user_registeration(self):
        # data below replaces the request data json in the register route to test
        data = {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "password"
        }

        # teling it that it's a json request ,
        response = self.client.post('/auth/signup', json = data)

        user = User.query.filter_by(email='testuser@gmail.com').first()

        # checking if this user has a sueraem testuser
        assert user.username == "testuser"

        assert response.status_code == 201


    def test_user_login(self):
        data = {
            "email": "testuser@gmail.com",
            "password": "password"
        }

        response = self.client.post('/auth/login', json = data)

        assert response.status_code == 200

    

    