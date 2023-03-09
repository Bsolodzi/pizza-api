from flask_restx import Namespace, Resource, fields
from ..models.orders import Order
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.users import User
from ..utils import db

order_namespace = Namespace('orders', description= 'name space for orders')

order_model = order_namespace.model(
    'Order', {
        'id': fields.Integer(description='An ID'),
        'size': fields.String(description= 'Size of order', required = True, 
                             enum=['SMALL','MEDIUM','LARGE','EXTRA_LARGE']
        ),
        'order_status': fields.String(description='The Status of our Order', required= True,
                                      enum= ['PENDING', 'IN_TRANSIT','DELIVERED']
        ),
        'flavour': fields.String(description= 'Flavour of pizza', required = True),
        'quantity' : fields.Integer(description= 'Quantity of pizza', required = True)
    }
)

order_status_model = order_namespace.model(
    'OrderStatus', {
        'order_status': fields.String(required=True, description = 'Order Status', 
                                      enum= ['PENDING', 'IN_TRANSIT','DELIVERED'] 
                                      )
    }
)

# get all orderes and also create an order
@order_namespace.route('/orders')
class OrderGetCreate(Resource):
    # marshall_with helps get AN OBJECT FROM THE DB
    # localhost:5000/orders/orders
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(
        description = "Get all orders",
    )
    @jwt_required()
    # get orders
    def get(self):
        """
            Get all orders
        """
        # returns an empty list of orders
        orders = Order.query.all()

        return orders, HTTPStatus.OK

    # localhost:5000/orders/orders
    # create orders
    @order_namespace.expect(order_model)
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(
        description = "Place an order",
    )
    @jwt_required()
    def post(self):
        """
            Place an order
        """
        username = get_jwt_identity()

        # gets the username if the current user and assign it to current user
        current_user = User.query.filter_by(username=username).first()

        # payload(funstions as get.json) tells us every information(payload) about the user
        data = order_namespace.payload

        new_order = Order(
            # getting the size from the payload
            size = data['size'],
            quantity = data['quantity'],
            flavour = data['flavour']
        )

        # use jwt_identity to get the user using the relationship created and now store as the user of the new order 
        new_order.user = current_user

        new_order.save()

        return new_order, HTTPStatus.CREATED

# localhost:5000/orders/order/order_id
@order_namespace.route('/order/<int:order_id>')
class GetUpdateDelete(Resource):
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(
        description = "Retreive an order by its id",
        params = {'order_id': "An ID for an order"}
    )
    @jwt_required()
    def get(self, order_id):
        """
            Retreiving an order by id
        """
        order = Order.get_by_id(order_id)

        return order, HTTPStatus.OK

    # we need to serialize the data in order to update
    @order_namespace.expect(order_model)
    # because we are printing something out
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(
        description = "Updating an order by id",
        params = {'order_id': "An ID for an order"}

    )

    # localhost:5000/orders/order/order_id
    @jwt_required()
    def put(self, order_id):
        """
            Update an order by id
        """
        order_to_update = Order.get_by_id(order_id)

        # getting all data about the order
        data = order_namespace.payload

        order_to_update.quantity = data["quantity"]
        order_to_update.size = data["size"]
        order_to_update.flavour = data["flavour"]

        # saving changes to the database only
        order_to_update.update()

        return order_to_update, HTTPStatus.OK

    @order_namespace.doc(
        description = "Delete an order by id",
        params = {'order_id': "An ID for an order"}

    )

    # localhost:5000/orders/order/order_id
    @jwt_required()
    def delete(self, order_id):
        """
            Delete an order
        """

        order_to_delete = Order.get_by_id(order_id)

        order_to_delete.delete()

        return {"message": "Deleted Successfully"}, HTTPStatus.OK

# localhost:5000/orders/user/user_id/order/order_id
# getting a specific order of a user
@order_namespace.route('/user/<int:user_id>/order/<int:order_id>')
class GetSpecificOrderbyUser(Resource):
    
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(
        description = "Get a user specific order by user id and order id",
        params = {'order_id': "An ID for an order", 'user_id': "An ID for the user"}
    )
    @jwt_required()
    def get(self, user_id, order_id):
        """
            Get a user specific order
        """
        # get user by user id
        user = User.get_by_id(user_id)
        
        # get order and if the current_user = user(gotten from above), then return the order else return null
        order = Order.query.filter_by(id=order_id).filter_by(user=user).first()

        return order, HTTPStatus.OK

# localhost:5000/orders/user/user_id/orders
# getting all the orders a user has made
@order_namespace.route('/user/<int:user_id>/orders')
class UserOrders(Resource):
    # marshall_list_with returns all the orders
    @order_namespace.marshal_list_with(order_model)
    @order_namespace.doc(
        description = "Get a user's orders by user id",
        params = {'user_id': "An ID for a user"}
    )
    @jwt_required()
    def get(self, user_id):
        """
            Get all user orders
        """
        user = User.get_by_id(user_id)

        orders = user.orders

        return orders, HTTPStatus.OK

# localhost:5000/orders/order/status/order_id
@order_namespace.route('/order/status/<int:order_id>')
class UpdateOrderStatus(Resource):
    @order_namespace.expect(order_status_model)
    # since we are returning use marshall
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(
        description = "Update an order status by order id",
        params = {'order_id': "An ID for an order"}
    )
    @jwt_required()
    #patch-partial update, put- full update
    def patch(self, order_id):
        """
            Update status of order
        """
        data = order_namespace.payload

        order_to_update = Order.get_by_id(order_id)

        order_to_update.order_status = data['order_status']

        order_to_update.update()

        return order_to_update, HTTPStatus.OK