import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import your models
from database import Base, Client, Product, Stock, Order, OrderItem, Shipment, ShipmentItem


# !!!!!!!!!!!!!!!!!!

# FIXTURE: In-memory database

# !!!!!!!!!!!!!!!!!!

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    TestingSession = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    session = TestingSession()
    yield session
    session.close()


# !!!!!!!!!!!!!!!!!!

# CLIENT TESTS

# !!!!!!!!!!!!!!!!!!

def test_create_client(db_session):
    client = Client(client_name="Test Client", client_address="123 St", contact_info="email@test.com")
    db_session.add(client)
    db_session.commit()

    assert client.client_id == 1
    assert client.client_name == "Test Client"


def test_client_product_relationship(db_session):
    client = Client(client_name="Client A")
    product = Product(product_name="Widget", sku="SKU1", client=client)

    db_session.add_all([client, product])
    db_session.commit()

    assert len(client.products) == 1
    assert client.products[0].product_name == "Widget"


# !!!!!!!!!!!!!!!!!!

# PRODUCT TESTS

# !!!!!!!!!!!!!!!!!!

def test_create_product(db_session):
    product = Product(product_name="Item", description="Desc", sku="ABC123")
    db_session.add(product)
    db_session.commit()

    assert product.product_id == 1
    assert product.sku == "ABC123"


def test_product_stock_relationship(db_session):
    product = Product(product_name="Item", sku="SKU")
    stock = Stock(product=product, quantity=50, location="A1")

    db_session.add_all([product, stock])
    db_session.commit()

    assert product.stock[0].quantity == 50
    assert stock.product.product_name == "Item"


# !!!!!!!!!!!!!!!!!!

# STOCK TESTS

# !!!!!!!!!!!!!!!!!!

def test_create_stock(db_session):
    product = Product(product_name="Item", sku="SKU")
    stock = Stock(product=product, quantity=10, location="Shelf 1")

    db_session.add_all([product, stock])
    db_session.commit()

    assert stock.stock_id == 1
    assert stock.quantity == 10


# !!!!!!!!!!!!!!!!!!

# ORDER TESTS

# !!!!!!!!!!!!!!!!!!

def test_create_order(db_session):
    client = Client(client_name="Client A")
    db_session.add(client)
    db_session.commit()

    order = Order(client_id=client.client_id, order_status="pending")
    db_session.add(order)
    db_session.commit()

    assert order.order_id == 1
    assert order.client_id == client.client_id
    assert order.order_status == "pending"


def test_order_item_relationship(db_session):
    client = Client(client_name="Client A")
    product = Product(product_name="Item", sku="SKU")
    db_session.add_all([client, product])
    db_session.commit()

    order = Order(client_id=client.client_id, order_status="pending")
    db_session.add(order)
    db_session.commit()

    item = OrderItem(order_id=order.order_id, product_id=product.product_id, quantity=5)
    db_session.add(item)
    db_session.commit()

    assert len(order.items) == 1
    assert order.items[0].quantity == 5


# !!!!!!!!!!!!!!!!!!

# SHIPMENT TESTS

# !!!!!!!!!!!!!!!!!!

def test_create_shipment(db_session):
    client = Client(client_name="Client A")
    db_session.add(client)
    db_session.commit()

    order = Order(client_id=client.client_id, order_status="pending")
    db_session.add(order)
    db_session.commit()

    shipment = Shipment(order_id=order.order_id, shipment_status="pending")
    db_session.add(shipment)
    db_session.commit()

    assert shipment.shipment_id == 1
    assert shipment.order_id == order.order_id


def test_shipment_item_relationship(db_session):
    client = Client(client_name="Client A")
    product = Product(product_name="Item", sku="SKU")
    db_session.add_all([client, product])
    db_session.commit()

    order = Order(client_id=client.client_id, order_status="pending")
    db_session.add(order)
    db_session.commit()

    shipment = Shipment(order_id=order.order_id, shipment_status="pending")
    db_session.add(shipment)
    db_session.commit()

    item = ShipmentItem(shipment_id=shipment.shipment_id, product_id=product.product_id, quantity=3)
    db_session.add(item)
    db_session.commit()

    assert len(shipment.items) == 1
    assert shipment.items[0].quantity == 3


# !!!!!!!!!!!!!!!!!!

# FOREIGN KEY INTEGRITY TESTS

# !!!!!!!!!!!!!!!!!!

def test_foreign_key_links(db_session):
    client = Client(client_name="Client A")
    product = Product(product_name="Item", sku="SKU", client=client)
    db_session.add_all([client, product])
    db_session.commit()

    order = Order(client_id=client.client_id, order_status="pending")
    db_session.add(order)
    db_session.commit()

    order_item = OrderItem(order_id=order.order_id, product_id=product.product_id, quantity=2)
    db_session.add(order_item)
    db_session.commit()

    assert order.client_id == client.client_id
    assert order_item.product_id == product.product_id
    assert order_item.order_id == order.order_id
