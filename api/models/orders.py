from ..utils import db
from enum import Enum
from datetime import datetime

# creating a class for sizes
class Sizes(Enum):
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'
    EXTRA_LARGE = 'extra_large'

# creating a class for order status
class OrderStatus(Enum):
    PENDING = 'pending'
    IN_TRANSIT = 'in-transit'
    DELIVERED = 'delivered'

class OrderFlavour(Enum):
    PEPPERONI = 'pepperroni'
    CHICKEN = 'chicken'
    PORK = 'pork'
    MIX = 'mix'

    

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer(), primary_key = True)
    size = db.Column(db.Enum(Sizes), default = Sizes.SMALL)
    order_status = db.Column(db.Enum(OrderStatus), default = OrderStatus.PENDING)
    flavour = db.Column(db.String(), nullable = False, default = OrderFlavour.MIX)
    quantity = db.Column(db.Integer())
    date_created = db.Column(db.DateTime(), default = datetime.utcnow)
    # linking order to user by getting the user's id
    customer = db.Column(db.Integer(), db.ForeignKey('users.id'))

    def __repr__(self):
        return f"<Order {self.id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    #cls represents the model and ca be represented by anything
    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)
    
    # function to update an order
    def update(self):
        db.session.commit()

    # function to delete an order
    def delete(self):
        db.session.delete(self)
        db.session.commit()