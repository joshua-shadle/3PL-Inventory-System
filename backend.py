from database import session, Client, Product, Stock, Order, OrderItem, Shipment, ShipmentItem


class ClientManager:

    def add(self, client_name, client_address, contact_info):
        new_client = Client(client_name=client_name, client_address=client_address, contact_info=contact_info)
        session.add(new_client)
        session.commit()
        return new_client

    def fetch_all(self):
        return session.query(Client).all()

    def fetch_by_id(self, client_id):
        return session.query(Client).filter_by(client_id=client_id).first()

    def update(self, client_id, client_name, client_address, contact_info):
        client = self.fetch_by_id(client_id)
        if client is None:
            return None
        client.client_name = client_name
        client.client_address = client_address
        client.contact_info = contact_info
        session.commit()
        return client

    def delete(self, client_id):
        client = self.fetch_by_id(client_id)
        if client is None:
            return False
        session.delete(client)
        session.commit()
        return True


class ProductManager:

    def add(self, product_name, description, sku):
        new_product = Product(product_name=product_name, description=description, sku=sku)
        session.add(new_product)
        session.commit()
        return new_product

    def fetch_all(self):
        return session.query(Product).all()

    def fetch_by_id(self, product_id):
        return session.query(Product).filter_by(product_id=product_id).first()

    def update(self, product_id, product_name, description, sku):
        product = self.fetch_by_id(product_id)
        if product is None:
            return None
        product.product_name = product_name
        product.description = description
        product.sku = sku
        session.commit()
        return product

    def delete(self, product_id):
        product = self.fetch_by_id(product_id)
        if product is None:
            return False
        session.delete(product)
        session.commit()
        return True


class StockManager:

    def add(self, product_id, quantity, location):
        new_stock = Stock(product_id=product_id, quantity=quantity, location=location)
        session.add(new_stock)
        session.commit()
        return new_stock

    def fetch_all(self):
        return session.query(Stock).all()

    def fetch_by_id(self, stock_id):
        return session.query(Stock).filter_by(stock_id=stock_id).first()

    def update(self, stock_id, quantity, location):
        stock = self.fetch_by_id(stock_id)
        if stock is None:
            return None
        stock.quantity = quantity
        stock.location = location
        session.commit()
        return stock

    def delete(self, stock_id):
        stock = self.fetch_by_id(stock_id)
        if stock is None:
            return False
        session.delete(stock)
        session.commit()
        return True

    def stock_level(self, product_id):
        # Returns total quantity across all stock rows for a given product
        rows = session.query(Stock).filter_by(product_id=product_id).all()
        total = 0
        for row in rows:
            total += row.quantity
        return total

    def low_stock_alert(self, threshold=10):
        # Returns a list of products whose total stock is at or below the threshold
        alerts = []
        products = session.query(Product).all()
        for product in products:
            total = self.stock_level(product.product_id)
            if total <= threshold:
                alerts.append({
                    "product_id": product.product_id,
                    "product_name": product.product_name,
                    "quantity": total
                })
        return alerts


class OrderManager:

    def add(self, client_id):
        new_order = Order(client_id=client_id, order_status='pending')
        session.add(new_order)
        session.commit()
        return new_order

    def fetch_all(self):
        return session.query(Order).all()

    def fetch_by_id(self, order_id):
        return session.query(Order).filter_by(order_id=order_id).first()

    def update(self, order_id, order_status):
        order = self.fetch_by_id(order_id)
        if order is None:
            return None
        order.order_status = order_status
        session.commit()
        return order

    def delete(self, order_id):
        order = self.fetch_by_id(order_id)
        if order is None:
            return False
        session.delete(order)
        session.commit()
        return True

    def commit_order(self, order_id):
        # Marks an order as committed, meaning it is ready to be fulfilled
        return self.update(order_id, 'committed')

    def get_order(self, order_id):
        # Returns an order and all its line items as a dictionary
        order = self.fetch_by_id(order_id)
        if order is None:
            return None
        items = []
        for item in order.items:
            items.append({
                "order_item_id": item.order_item_id,
                "product_id": item.product_id,
                "quantity": item.quantity
            })
        return {
            "order_id": order.order_id,
            "client_id": order.client_id,
            "order_status": order.order_status,
            "items": items
        }


class OrderItemManager:
    def fetch_by_order(self, order_id):
        return session.query(OrderItem).filter_by(order_id=order_id).all()

    def add(self, order_id, product_id, quantity):
        new_item = OrderItem(order_id=order_id, product_id=product_id, quantity=quantity)
        session.add(new_item)
        session.commit()
        return new_item

    def fetch_all(self):
        return session.query(OrderItem).all()

    def fetch_by_id(self, order_item_id):
        return session.query(OrderItem).filter_by(order_item_id=order_item_id).first()

    def update(self, order_item_id, quantity):
        item = self.fetch_by_id(order_item_id)
        if item is None:
            return None
        item.quantity = quantity
        session.commit()
        return item

    def delete(self, order_item_id):
        item = self.fetch_by_id(order_item_id)
        if item is None:
            return False
        session.delete(item)
        session.commit()
        return True


class ShipmentManager:

    def add(self, order_id):
        new_shipment = Shipment(order_id=order_id, shipment_status='pending')
        session.add(new_shipment)
        session.commit()
        return new_shipment

    def fetch_all(self):
        return session.query(Shipment).all()

    def fetch_by_id(self, shipment_id):
        return session.query(Shipment).filter_by(shipment_id=shipment_id).first()

    def update(self, shipment_id, shipment_status):
        shipment = self.fetch_by_id(shipment_id)
        if shipment is None:
            return None
        shipment.shipment_status = shipment_status
        session.commit()
        return shipment

    def delete(self, shipment_id):
        shipment = self.fetch_by_id(shipment_id)
        if shipment is None:
            return False
        session.delete(shipment)
        session.commit()
        return True

    def check_status(self, shipment_id):
        shipment = self.fetch_by_id(shipment_id)
        if shipment is None:
            return None
        return shipment.shipment_status

    def mark_as_shipped(self, shipment_id):
        return self.update(shipment_id, 'shipped')

    def mark_as_delivered(self, shipment_id):
        return self.update(shipment_id, 'delivered')


class ShipmentItemManager:

    def add(self, shipment_id, product_id, quantity):
        new_item = ShipmentItem(shipment_id=shipment_id, product_id=product_id, quantity=quantity)
        session.add(new_item)
        session.commit()
        return new_item

    def fetch_all(self):
        return session.query(ShipmentItem).all()

    def fetch_by_id(self, shipment_item_id):
        return session.query(ShipmentItem).filter_by(shipment_item_id=shipment_item_id).first()

    def update(self, shipment_item_id, quantity):
        item = self.fetch_by_id(shipment_item_id)
        if item is None:
            return None
        item.quantity = quantity
        session.commit()
        return item

    def delete(self, shipment_item_id):
        item = self.fetch_by_id(shipment_item_id)
        if item is None:
            return False
        session.delete(item)
        session.commit()
        return True