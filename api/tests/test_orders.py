import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from ..models.orders import Order
from flask_jwt_extended import create_access_token

class OrderTestCase(unittest.TestCase):
    def setUp(self):

        self.app = create_app(config=config_dict['test'])

        self.appctx = self.app.app_context()
        
        self.appctx.push()

        self.client = self.app.test_client()

        db.create_all()

    def tearDown(self):
        db.drop_all()

        self.app = None

        self.client = None

        self.appctx.pop()

    # testing route for getting all others
    def test_get_all_orders(self):
        # since it is a protected route, create an access token using identity testuser
        token = create_access_token(identity="testuser")

        # using the header way of inputting auth tokens to login a user rather than the normal bearer way
        headers = {
            "Authorization": f"Bearer {token}"
        }

        # using the get method to get the data from db 
        response = self.client.get('/orders/orders', headers= headers)

        # checks if the status code is 200 and
        assert response.status_code == 200
        
        # check if the data is also empty then we know our route is correct
        assert response.json == []

    # function to test the creation of an order
    def test_create_order_(self):
        # fake data to be passed into the db 
        data = {
            "size": "SMALL",
            "quantity": 1,
            "flavour":"Pepperroni"
        }
        
        # since it is a protected route, create an access token using identity testuser
        token = create_access_token(identity="testuser")

        # using the header way of inputing auth tokens to authenticate a user rather than the normal bearer way
        headers = {
            "Authorization": f"Bearer {token}"
        }

        # using the response to post/push the json data into the db and then the header(token) 
        response = self.client.post('/orders/orders', json=data, headers=headers)

        # checks if status code is == 201. if yes, we are succesfull
        assert response.status_code == 201

        # from our memory db, total orders is only one
        orders = Order.query.all()

        # checks if the orders in db ==1, else returns failed 
        assert len(orders)== 1

        # checking if the size is small
        assert response.json['size'] == 'Sizes.SMALL'

    # function to test get an order by id
    def test_get_order_by_id(self):

        order = Order (
            size = 'LARGE',
            flavour = "Pepperoni",
            quantity = 2
        )

        order.save()

        token = create_access_token(identity="testuser")
        
        # using the header way of inputing auth tokens to authenticate a user rather than the normal bearer way
        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = self.client.get('/orders/order/1', headers=headers)

        assert response.status_code == 200
