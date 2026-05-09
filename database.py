from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine

engine = create_engine('sqlite:///db.sqlite')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class Client(Base):
    __tablename__ = 'client'
    client_id = Column(Integer, primary_key=True)
    client_name = Column(String)
    client_address = Column(String)
    contact_info = Column(String)

    products = relationship("Product", backref="client")


class Product(Base):
    __tablename__ = 'product'
    product_id = Column(Integer, primary_key=True)
    product_name = Column(String)
    description = Column(String)
    sku = Column(String)  # FIXED
    client_id = Column(Integer, ForeignKey('client.client_id'))

    stock = relationship("Stock", backref="product")
    order_items = relationship("OrderItem", backref="product")
    shipment_items = relationship("ShipmentItem", backref="product")


class Stock(Base):
    __tablename__ = 'stock'
    stock_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.product_id'))
    quantity = Column(Integer)
    location = Column(String)  # FIXED


class Order(Base):
    __tablename__ = 'order'
    order_id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client.client_id'))  # FIXED
    order_status = Column(String)

    items = relationship("OrderItem", backref="order")
    shipment = relationship("Shipment", backref="order", uselist=False)


class OrderItem(Base):
    __tablename__ = 'order_item'
    order_item_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order.order_id'))
    product_id = Column(Integer, ForeignKey('product.product_id'))
    quantity = Column(Integer)


class Shipment(Base):
    __tablename__ = 'shipment'
    shipment_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order.order_id'))
    shipment_status = Column(String)

    items = relationship("ShipmentItem", backref="shipment")


class ShipmentItem(Base):
    __tablename__ = 'shipment_item'
    shipment_item_id = Column(Integer, primary_key=True)
    shipment_id = Column(Integer, ForeignKey('shipment.shipment_id'))
    product_id = Column(Integer, ForeignKey('product.product_id'))
    quantity = Column(Integer)


Base.metadata.create_all(engine)