import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import your models + Base
from database import Base, Client, Product, Stock, Order, OrderItem, Shipment, ShipmentItem

# Import your managers
from backend import (
    ClientManager,
    ProductManager,
    StockManager,
    OrderManager,
    OrderItemManager,
    ShipmentManager,
    ShipmentItemManager
)

# !!!!!!!!!!!!!!!!!!

# FIXTURE: In‑memory database

# !!!!!!!!!!!!!!!!!!

@pytest.fixture(scope="function")
def test_session(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()

    Base.metadata.create_all(engine)

    # Patch the global session used in backend.py
    monkeypatch.setattr("backend.session", session)

    return session


# !!!!!!!!!!!!!!!!!!

# CLIENT TESTS

# !!!!!!!!!!!!!!!!!!

def test_add_client(test_session):
    cm = ClientManager()
    client = cm.add("John", "123 St", "john@example.com")

    assert client.client_id == 1
    assert client.client_name == "John"


def test_update_client(test_session):
    cm = ClientManager()
    c = cm.add("Old", "Addr", "old@mail")

    updated = cm.update(c.client_id, "New", "NewAddr", "new@mail")
    assert updated.client_name == "New"


def test_delete_client(test_session):
    cm = ClientManager()
    c = cm.add("A", "B", "C")

    assert cm.delete(c.client_id) is True
    assert cm.fetch_by_id(c.client_id) is None


# !!!!!!!!!!!!!!!!!!

# PRODUCT TESTS

# !!!!!!!!!!!!!!!!!!

def test_add_product(test_session):
    pm = ProductManager()
    p = pm.add("Laptop", "Dell", "SKU1")

    assert p.product_id == 1
    assert p.sku == "SKU1"


def test_update_product(test_session):
    pm = ProductManager()
    p = pm.add("Old", "Desc", "SKU")

    updated = pm.update(p.product_id, "New", "NewDesc", "SKU2")
    assert updated.product_name == "New"


# !!!!!!!!!!!!!!!!!!

# STOCK TESTS

# !!!!!!!!!!!!!!!!!!

def test_stock_add_and_level(test_session):
    pm = ProductManager()
    sm = StockManager()

    p = pm.add("Item", "Desc", "SKU")
    sm.add(p.product_id, 5, "A")
    sm.add(p.product_id, 7, "B")

    assert sm.stock_level(p.product_id) == 12


def test_low_stock_alert(test_session):
    pm = ProductManager()
    sm = StockManager()

    p = pm.add("Item", "Desc", "SKU")
    sm.add(p.product_id, 3, "A")

    alerts = sm.low_stock_alert(threshold=5)
    assert len(alerts) == 1
    assert alerts[0]["product_id"] == p.product_id


# !!!!!!!!!!!!!!!!!!

# ORDER TESTS

# !!!!!!!!!!!!!!!!!!

def test_order_creation_and_commit(test_session):
    cm = ClientManager()
    om = OrderManager()

    c = cm.add("John", "Addr", "Mail")
    order = om.add(c.client_id)

    assert order.order_status == "pending"

    om.commit_order(order.order_id)
    assert om.fetch_by_id(order.order_id).order_status == "committed"


# !!!!!!!!!!!!!!!!!!

# ORDER ITEM TESTS

# !!!!!!!!!!!!!!!!!!

def test_order_item_add(test_session):
    cm = ClientManager()
    pm = ProductManager()
    om = OrderManager()
    oim = OrderItemManager()

    c = cm.add("John", "Addr", "Mail")
    p = pm.add("Laptop", "Desc", "SKU")
    order = om.add(c.client_id)

    item = oim.add(order.order_id, p.product_id, 2)
    assert item.quantity == 2


# !!!!!!!!!!!!!!!!!!

# SHIPMENT TESTS

# !!!!!!!!!!!!!!!!!!

def test_shipment_flow(test_session):
    cm = ClientManager()
    pm = ProductManager()
    om = OrderManager()
    sm = ShipmentManager()

    c = cm.add("John", "Addr", "Mail")
    p = pm.add("Laptop", "Desc", "SKU")
    order = om.add(c.client_id)

    shipment = sm.add(order.order_id)
    assert shipment.shipment_status == "pending"

    sm.mark_as_shipped(shipment.shipment_id)
    assert sm.check_status(shipment.shipment_id) == "shipped"


# !!!!!!!!!!!!!!!!!!

# SHIPMENT ITEM TESTS

# !!!!!!!!!!!!!!!!!!

def test_shipment_item_add(test_session):
    cm = ClientManager()
    pm = ProductManager()
    om = OrderManager()
    sm = ShipmentManager()
    sim = ShipmentItemManager()

    c = cm.add("John", "Addr", "Mail")
    p = pm.add("Laptop", "Desc", "SKU")
    order = om.add(c.client_id)
    shipment = sm.add(order.order_id)

    item = sim.add(shipment.shipment_id, p.product_id, 4)
    assert item.quantity == 4
