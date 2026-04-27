# tests/test_database.py
"""Tests for database"""
import pytest
from database import session, Client, Product, Stock, Order, OrderItem, Shipment, ShipmentItem

def test_client_model():
    c = Client(client_name="Test", client_address="Addr", contact_info="Contact")
    session.add(c)
    session.commit()
    assert c.client_id is not None


def test_product_model():
    p = Product(product_name="Laptop", description="Desc", sku="SKU123")
    session.add(p)
    session.commit()
    assert p.sku == "SKU123"


def test_stock_model(products=None):
    p = Product(product_name="Mouse", description="Wireless", sku="SKU999")
    session.add(p)
    session.commit()

    s = Stock(product_id=p.product_id, quantity=10, location="A1")
    session.add(s)
    session.commit()

    assert s.location == "A1"


def test_order_model():
    c = Client(client_name="Client", client_address="Addr", contact_info="Contact")
    session.add(c)
    session.commit()

    o = Order(client_id=c.client_id, order_status="pending")
    session.add(o)
    session.commit()

    assert o.order_status == "pending"


def test_relationships():
    c = Client(client_name="RelTest", client_address="Addr", contact_info="Contact")
    session.add(c)
    session.commit()

    p = Product(product_name="Item", description="Desc", sku="SKU1", client_id=c.client_id)
    session.add(p)
    session.commit()

    assert p.client.client_name == "RelTest"
