import tkinter as tk
from tkinter import ttk, messagebox

# ---------- Style constants ----------

STYLE_BG = "#f4f4f4"
NAV_BG = "#2c3e50"
NAV_BTN_BG = "#34495e"
NAV_BTN_FG = "white"
CONTENT_BG = "white"
ACCENT = "#2980b9"

FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_SUBTITLE = ("Segoe UI", 12)
FONT_NORMAL = ("Segoe UI", 10)


# ---------- Popup windows ----------

class CreateOrderWindow(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.title("Create Order")
        self.geometry("400x300")
        self.configure(bg=CONTENT_BG)

        tk.Label(self, text="Create New Order", font=("Segoe UI", 14), bg=CONTENT_BG).pack(pady=10)

        form = tk.Frame(self, bg=CONTENT_BG)
        form.pack(pady=10)

        tk.Label(form, text="Client ID:", bg=CONTENT_BG).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.client_entry = tk.Entry(form, width=30)
        self.client_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(self, text="Create Order", bg=ACCENT, fg="white",
                  command=self.create_order).pack(pady=15)

    def create_order(self):
        client_id = self.client_entry.get().strip()
        if not client_id.isdigit():
            messagebox.showwarning("Invalid", "Client ID must be a number")
            return

        om = self.controller.order_manager
        order = om.add(int(client_id))
        messagebox.showinfo("Order Created", f"Order #{order.order_id} created")
        self.destroy()


class AddItemWindow(tk.Toplevel):
    def __init__(self, parent, controller, order_id):
        super().__init__(parent)
        self.controller = controller
        self.order_id = order_id

        self.title(f"Add Item to Order #{order_id}")
        self.geometry("350x250")
        self.configure(bg=CONTENT_BG)

        tk.Label(self, text="Add Item to Order", font=("Segoe UI", 14), bg=CONTENT_BG).pack(pady=10)

        form = tk.Frame(self, bg=CONTENT_BG)
        form.pack(pady=10)

        tk.Label(form, text="Product ID:", bg=CONTENT_BG).grid(row=0, column=0, sticky="w", pady=5)
        self.product_entry = tk.Entry(form, width=20)
        self.product_entry.grid(row=0, column=1, pady=5)

        tk.Label(form, text="Quantity:", bg=CONTENT_BG).grid(row=1, column=0, sticky="w", pady=5)
        self.qty_entry = tk.Entry(form, width=20)
        self.qty_entry.grid(row=1, column=1, pady=5)

        tk.Button(self, text="Add Item", width=18, bg=ACCENT, fg="white",
                  command=self.add_item).pack(pady=15)

    def add_item(self):
        product_id = self.product_entry.get().strip()
        qty = self.qty_entry.get().strip()

        # Validate numeric input
        if not product_id.isdigit() or not qty.isdigit():
            messagebox.showwarning("Invalid Input", "Product ID and Quantity must be numbers")
            return

        product_id = int(product_id)
        qty = int(qty)

        pm = self.controller.product_manager
        sm = self.controller.stock_manager
        oim = self.controller.order_item_manager

        # 1. Validate product exists in the database
        product = pm.fetch_by_id(product_id)
        if not product:
            messagebox.showerror("Invalid Product", f"Product ID {product_id} does not exist in the database")
            return

        # 2. Check stock level
        current_stock = sm.stock_level(product_id)
        if current_stock < qty:
            messagebox.showerror(
                "Insufficient Stock",
                f"Only {current_stock} units available for {product.product_name}"
            )
            return

        # 3. Subtract stock
        sm.clear_stock_for_product(product_id)

        new_stock = current_stock - qty
        location = product.stock[0].location if product.stock else "A1"
        sm.add(product_id, new_stock, location)

        # 4. Add item to order
        oim.add(self.order_id, product_id, qty)

        # 5. Low stock warning
        if new_stock < 15:
            messagebox.showwarning(
                "Low Stock Alert",
                f"{product.product_name} (SKU {product.sku}) is low on stock.\n"
                f"Remaining quantity: {new_stock}"
            )

        messagebox.showinfo("Item Added", f"{qty} x Product {product_id} added to Order #{self.order_id}")

        # Refresh Orders screen
        parent = self.master
        parent.load_orders()

        self.destroy()



class CreateShipmentWindow(tk.Toplevel):
    def __init__(self, parent, controller, order_id):
        super().__init__(parent)
        self.controller = controller
        self.order_id = order_id

        self.title("Create Shipment")
        self.geometry("400x300")
        self.configure(bg=CONTENT_BG)

        tk.Label(self, text=f"Create Shipment for Order #{order_id}", font=("Segoe UI", 14), bg=CONTENT_BG).pack(pady=10)

        tk.Button(self, text="Create Shipment", bg=ACCENT, fg="white",
                  command=self.create_shipment).pack(pady=15)

    def create_shipment(self):
        sm = self.controller.shipment_manager
        shipment = sm.add(self.order_id)
        messagebox.showinfo("Shipment Created", f"Shipment #{shipment.shipment_id} created")
        self.destroy()


class InventoryReportWindow(tk.Toplevel):
    def __init__(self, controller):
        super().__init__(controller)
        self.title("Inventory Report")
        self.geometry("700x500")
        self.configure(bg=CONTENT_BG)

        tk.Label(self, text="Inventory Report", font=("Segoe UI", 16), bg=CONTENT_BG).pack(pady=10)

        columns = ("Product", "SKU", "Quantity", "Locations")
        table = ttk.Treeview(self, columns=columns, show="headings", height=15)

        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=150, anchor="center")

        table.pack(pady=10, fill="both", expand=True)

        pm = controller.product_manager
        sm = controller.stock_manager

        # ---------- STACKING LOGIC ----------
        stacked = {}

        for product in pm.fetch_all():
            total_qty = sm.stock_level(product.product_id)
            locations = [s.location for s in product.stock]

            key = (product.product_name.lower().strip(),
                   product.sku.lower().strip())

            if key not in stacked:
                stacked[key] = {
                    "name": product.product_name,
                    "sku": product.sku,
                    "quantity": total_qty,
                    "locations": set(locations)
                }
            else:
                stacked[key]["quantity"] += total_qty
                stacked[key]["locations"].update(locations)

        # ---------- INSERT STACKED ROWS ----------
        for data in stacked.values():
            table.insert("", "end", values=(
                data["name"],
                data["sku"],
                data["quantity"],
                ", ".join(sorted(data["locations"]))
            ))



class LowStockReportWindow(tk.Toplevel):
    def __init__(self, controller):
        super().__init__(controller)
        self.title("Low Stock Report")
        self.geometry("600x450")
        self.configure(bg=CONTENT_BG)

        tk.Label(self, text="Low Stock Report", font=("Segoe UI", 16), bg=CONTENT_BG).pack(pady=10)

        columns = ("Product", "SKU", "Quantity")
        table = ttk.Treeview(self, columns=columns, show="headings", height=15)

        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=180, anchor="center")

        table.pack(pady=10, fill="both", expand=True)

        sm = controller.stock_manager
        pm = controller.product_manager

        alerts = sm.low_stock_alert(threshold=10)

        # ---------- STACKING LOGIC ----------
        stacked = {}

        for alert in alerts:
            product = pm.fetch_by_id(alert["product_id"])
            if not product:
                continue

            key = (product.product_name.lower().strip(),
                   product.sku.lower().strip())

            if key not in stacked:
                stacked[key] = {
                    "name": product.product_name,
                    "sku": product.sku,
                    "quantity": alert["quantity"]
                }
            else:
                stacked[key]["quantity"] += alert["quantity"]

        # ---------- INSERT STACKED ROWS ----------
        for data in stacked.values():
            table.insert("", "end", values=(
                data["name"],
                data["sku"],
                data["quantity"]
            ))




class SearchResultsWindow(tk.Toplevel):
    def __init__(self, parent, query, results):
        super().__init__(parent)
        self.title(f"Search Results for '{query}'")
        self.geometry("500x400")
        self.configure(bg=CONTENT_BG)

        tk.Label(self, text=f"Results for: {query}", font=("Segoe UI", 14), bg=CONTENT_BG).pack(pady=10)

        if not results:
            tk.Label(self, text="No results found.", font=FONT_NORMAL, bg=CONTENT_BG).pack(pady=20)
            return

        listbox = tk.Listbox(self, width=60, height=15)
        listbox.pack(pady=10, fill="both", expand=True)

        for r in results:
            listbox.insert(tk.END, r)


# ---------- Base screen ----------

class BaseScreen(tk.Frame):
    def __init__(self, parent, controller, title):
        super().__init__(parent, bg=STYLE_BG)
        self.controller = controller

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        title_bar = tk.Label(self, text=title, font=FONT_TITLE, bg=STYLE_BG)
        title_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=20)

        self.content = tk.Frame(self, bg=CONTENT_BG, bd=1, relief="solid")
        self.content.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)


# ---------- Main app ----------

class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()

        from backend import (
            ProductManager,
            ClientManager,
            StockManager,
            OrderManager,
            OrderItemManager,
            ShipmentManager,
        )

        self.product_manager = ProductManager()
        self.client_manager = ClientManager()
        self.stock_manager = StockManager()
        self.order_manager = OrderManager()
        self.order_item_manager = OrderItemManager()
        self.shipment_manager = ShipmentManager()

        self.title("3PL Inventory Management System")
        self.geometry("1000x650")
        self.configure(bg=STYLE_BG)

        self.status = tk.Label(self, text="Ready", anchor="w", bg="#eeeeee", font=FONT_NORMAL)
        self.status.pack(side="bottom", fill="x")

        self.create_navbar()

        self.container = tk.Frame(self, bg=STYLE_BG)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for FrameClass in (
            DashboardScreen,
            ProductsScreen,
            ClientsScreen,
            OrdersScreen,
            ShipmentsScreen,
            ReportsScreen,
        ):
            frame = FrameClass(self.container, self)
            self.frames[FrameClass.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("DashboardScreen")

    def create_navbar(self):
        nav = tk.Frame(self, bg=NAV_BG, height=50)
        nav.pack(side="top", fill="x")

        nav.grid_columnconfigure(0, weight=1)
        nav.grid_columnconfigure(1, weight=0)

        btn_frame = tk.Frame(nav, bg=NAV_BG)
        btn_frame.grid(row=0, column=0, sticky="w", padx=10)

        buttons = [
            ("Dashboard", "DashboardScreen"),
            ("Products", "ProductsScreen"),
            ("Clients", "ClientsScreen"),
            ("Orders", "OrdersScreen"),
            ("Shipments", "ShipmentsScreen"),
            ("Reports", "ReportsScreen"),
        ]

        for i, (text, screen_name) in enumerate(buttons):
            tk.Button(
                btn_frame,
                text=text,
                bg=NAV_BTN_BG,
                fg=NAV_BTN_FG,
                activebackground=ACCENT,
                activeforeground="white",
                relief="flat",
                font=("Segoe UI", 11),
                width=12,
                command=lambda name=screen_name: self.show_frame(name)
            ).grid(row=0, column=i, padx=2, pady=8)

        search_frame = tk.Frame(nav, bg=NAV_BG)
        search_frame.grid(row=0, column=1, sticky="e", padx=10)

        self.search_var = tk.StringVar()

        tk.Entry(search_frame, textvariable=self.search_var, width=25).pack(side="left", padx=5)

        tk.Button(
            search_frame,
            text="Search",
            bg=ACCENT,
            fg="white",
            relief="flat",
            command=self.perform_search
        ).pack(side="left")

    def perform_search(self):
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Search", "Enter a search term")
            return

        results = []

        # Products
        for p in self.product_manager.fetch_all():
            if query.lower() in p.product_name.lower() or query.lower() in p.sku.lower():
                results.append(f"Product: {p.product_name} (SKU: {p.sku})")

        # Clients
        for c in self.client_manager.fetch_all():
            if query.lower() in c.client_name.lower():
                results.append(f"Client: {c.client_name}")

        # Orders
        for o in self.order_manager.fetch_all():
            if query.lower() in str(o.order_id):
                results.append(f"Order #{o.order_id} (Status: {o.order_status})")

        # Shipments
        for s in self.shipment_manager.fetch_all():
            if query.lower() in str(s.shipment_id):
                results.append(f"Shipment #{s.shipment_id} (Status: {s.shipment_status})")

        SearchResultsWindow(self, query, results)

    def show_frame(self, screen_name):
        frame = self.frames[screen_name]

        if hasattr(frame, "load_products"):
            frame.load_products()
        if hasattr(frame, "load_clients"):
            frame.load_clients()
        if hasattr(frame, "load_orders"):
            frame.load_orders()
        if hasattr(frame, "load_shipments"):
            frame.load_shipments()

        frame.tkraise()
        self.status.config(text=f"Viewing: {screen_name.replace('Screen', '')}")


# ---------- Screens ----------

class DashboardScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "3PL Inventory Dashboard")

        center = tk.Frame(self.content, bg=CONTENT_BG)
        center.grid(row=0, column=0)

        tk.Label(center, text="Welcome to the Inventory Management System",
                 font=("Segoe UI", 14), bg=CONTENT_BG).pack(pady=10)

        tk.Label(center,
                 text="Use the navigation bar to manage products, clients, orders, shipments, and reports.",
                 font=FONT_SUBTITLE, bg=CONTENT_BG).pack(pady=5)


class ProductsScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Products / Inventory")

        center = tk.Frame(self.content, bg=CONTENT_BG)
        center.grid(row=0, column=0)

        form_frame = tk.Frame(center, bg=CONTENT_BG)
        form_frame.pack(pady=10)

        labels = ["Product Name:", "SKU:", "Quantity:", "Location:"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label, bg=CONTENT_BG, font=FONT_NORMAL)\
                .grid(row=i, column=0, sticky="e", padx=10, pady=5)

            entry = tk.Entry(form_frame, width=40)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[label] = entry

        btn_frame = tk.Frame(center, bg=CONTENT_BG)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Product", width=15, bg=ACCENT, fg="white",
                  command=self.add_product).grid(row=0, column=0, padx=5)

        tk.Button(btn_frame, text="Update Product", width=15, bg="#27ae60", fg="white",
                  command=self.update_product).grid(row=0, column=1, padx=5)

        tk.Button(btn_frame, text="Delete Product", width=15, bg="#c0392b", fg="white",
                  command=self.delete_product).grid(row=0, column=2, padx=5)

        columns = ("ID", "Name", "SKU", "Quantity", "Location")
        self.table = ttk.Treeview(center, columns=columns, show="headings", height=10)
        self.table.column("ID", width=0, stretch=False)
        self.table.heading("ID", text="")

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=180, anchor="center")

        self.table.pack(pady=10)
        self.table.bind("<<TreeviewSelect>>", self.load_selected_product)

        self.load_products()

    def load_products(self):
        # Clear table
        for row in self.table.get_children():
            self.table.delete(row)

        pm = self.controller.product_manager
        sm = self.controller.stock_manager

        stacked = {}

        for product in pm.fetch_all():
            total_qty = sm.stock_level(product.product_id)
            locations = [s.location for s in product.stock]

            key = (product.product_name.lower().strip(),
                   product.sku.lower().strip())

            if key not in stacked:
                stacked[key] = {
                    "id": product.product_id,
                    "name": product.product_name,
                    "sku": product.sku,
                    "quantity": total_qty,
                    "locations": set(locations)
                }
            else:
                stacked[key]["quantity"] += total_qty
                stacked[key]["locations"].update(locations)

        # Insert stacked rows
        for data in stacked.values():
            self.table.insert("", "end", values=(
                data["id"],  # REAL ID
                data["name"],
                data["sku"],
                data["quantity"],
                ", ".join(sorted(data["locations"]))
            ))

    def add_product(self):
        name = self.entries["Product Name:"].get().strip()
        sku = self.entries["SKU:"].get().strip()
        quantity = self.entries["Quantity:"].get().strip()
        location = self.entries["Location:"].get().strip()

        if not name or not sku:
            messagebox.showwarning("Missing Info", "Product Name and SKU are required")
            return

        pm = self.controller.product_manager
        sm = self.controller.stock_manager

        product = pm.add(name, "", sku)

        if quantity.isdigit():
            sm.add(product.product_id, int(quantity), location or "A1")

        self.clear_entries()
        self.load_products()
        messagebox.showinfo("Success", "Product added successfully")

    def load_selected_product(self, event):
        selected = self.table.selection()
        if not selected:
            return

        values = self.table.item(selected[0], "values")

        # Must be exactly 5 values
        if len(values) != 5:
            print("ERROR: Row does not contain 5 values:", values)
            return

        self.clear_entries()

        # Unpack values
        _, name, sku, qty, loc = values

        self.entries["Product Name:"].insert(0, name)
        self.entries["SKU:"].insert(0, sku)
        self.entries["Quantity:"].insert(0, qty)
        self.entries["Location:"].insert(0, loc)

    def delete_product(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a product to delete")
            return

        values = self.table.item(selected[0], "values")
        product_id = int(values[0])  # first column is ID

        pm = self.controller.product_manager
        sm = self.controller.stock_manager

        product = pm.fetch_by_id(product_id)
        if not product:
            messagebox.showwarning("Not Found", "Product not found in database")
            return

        sm.clear_stock_for_product(product_id)
        pm.delete(product_id)

        self.clear_entries()
        self.load_products()
        messagebox.showinfo("Deleted", "Product deleted successfully")

    def clear_entries(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def update_product(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a product to update")
            return

        values = self.table.item(selected[0], "values")

        # values[0] now contains ALL IDs, like "5,7,12"
        product_ids = [int(x) for x in values[0].split(",")]

        name = self.entries["Product Name:"].get().strip()
        sku = self.entries["SKU:"].get().strip()
        quantity = self.entries["Quantity:"].get().strip()
        location = self.entries["Location:"].get().strip()

        if not name or not sku:
            messagebox.showwarning("Missing Info", "Product Name and SKU are required")
            return

        pm = self.controller.product_manager
        sm = self.controller.stock_manager

        # Update ALL products in the stack
        for pid in product_ids:
            product = pm.fetch_by_id(pid)
            if product:
                pm.update(pid, name, product.description, sku)
                sm.clear_stock_for_product(pid)

        # Add NEW stock to the FIRST product ID
        if quantity.isdigit():
            sm.add(product_ids[0], int(quantity), location or "A1")

        self.clear_entries()
        self.load_products()
        messagebox.showinfo("Updated", "Product updated successfully")


class ClientsScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Clients")

        center = tk.Frame(self.content, bg=CONTENT_BG)
        center.grid(row=0, column=0)

        # ---------- Form ----------
        form_frame = tk.Frame(center, bg=CONTENT_BG)
        form_frame.pack(pady=10)

        labels = ["Client Name:", "Address:", "Contact Info:"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label, bg=CONTENT_BG, font=FONT_NORMAL)\
                .grid(row=i, column=0, sticky="e", padx=10, pady=5)

            entry = tk.Entry(form_frame, width=40)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[label] = entry

        # ---------- Buttons ----------
        btn_frame = tk.Frame(center, bg=CONTENT_BG)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Client", width=15, bg=ACCENT, fg="white",
                  command=self.add_client).grid(row=0, column=0, padx=5)

        tk.Button(btn_frame, text="Update Client", width=15, bg="#27ae60", fg="white",
                  command=self.update_client).grid(row=0, column=1, padx=5)

        tk.Button(btn_frame, text="Delete Client", width=15, bg="#c0392b", fg="white",
                  command=self.delete_client).grid(row=0, column=2, padx=5)

        # ---------- Table ----------
        columns = ("ID", "Client Name", "Address", "Contact Info")
        self.table = ttk.Treeview(center, columns=columns, show="headings", height=12)

        self.table.column("ID", width=0, stretch=False)
        self.table.heading("ID", text="")

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=220, anchor="center")

        self.table.pack(pady=10)
        self.table.bind("<<TreeviewSelect>>", self.load_selected_client)

        self.load_clients()

    def load_clients(self):
        for row in self.table.get_children():
            self.table.delete(row)

        cm = self.controller.client_manager

        for client in cm.fetch_all():
            self.table.insert("", "end", values=(
                client.client_id,
                client.client_name,
                client.client_address,
                client.contact_info
            ))

    def load_selected_client(self, event):
        selected = self.table.selection()
        if selected:
            values = self.table.item(selected[0], "values")
            self.clear_entries()
            for (label, entry), value in zip(self.entries.items(), values[1:]):
                entry.insert(0, value)

    def add_client(self):
        name = self.entries["Client Name:"].get().strip()
        address = self.entries["Address:"].get().strip()
        contact = self.entries["Contact Info:"].get().strip()

        if not name:
            messagebox.showwarning("Missing Info", "Client Name is required")
            return

        cm = self.controller.client_manager
        cm.add(name, address, contact)

        self.clear_entries()
        self.load_clients()
        messagebox.showinfo("Success", "Client added successfully")

    def update_client(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a client to update")
            return

        values = self.table.item(selected[0], "values")
        client_id = int(values[0])

        name = self.entries["Client Name:"].get().strip()
        address = self.entries["Address:"].get().strip()
        contact = self.entries["Contact Info:"].get().strip()

        cm = self.controller.client_manager
        cm.update(client_id, name, address, contact)

        self.clear_entries()
        self.load_clients()
        messagebox.showinfo("Updated", "Client updated successfully")

    def delete_client(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a client to delete")
            return

        values = self.table.item(selected[0], "values")
        client_id = int(values[0])

        cm = self.controller.client_manager
        cm.delete(client_id)

        self.clear_entries()
        self.load_clients()
        messagebox.showinfo("Deleted", "Client deleted successfully")

    def clear_entries(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)



class OrdersScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Orders")

        center = tk.Frame(self.content, bg=CONTENT_BG)
        center.grid(row=0, column=0)

        columns = ("Order ID", "Client", "Status", "Items")
        self.table = ttk.Treeview(center, columns=columns, show="headings", height=12)
        self.table.bind("<<TreeviewSelect>>", self.show_order_items)

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=150, anchor="center")

        self.table.pack(pady=10)

        btn_frame = tk.Frame(center, bg=CONTENT_BG)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Create Order", width=18, bg=ACCENT, fg="white",
                  command=self.create_order_popup).grid(row=0, column=0, padx=5)

        tk.Button(btn_frame, text="Add Item to Order", width=18, bg="#27ae60", fg="white",
                  command=self.add_item_popup).grid(row=0, column=1, padx=5)

        tk.Button(btn_frame, text="Commit Order", width=18, bg="#8e44ad", fg="white",
                  command=self.commit_selected_order).grid(row=0, column=2, padx=5)

        tk.Button(btn_frame, text="Create Shipment", width=18, bg="#e67e22", fg="white",
                  command=self.create_shipment_popup).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Delete Order", width=18, bg="#c0392b", fg="white",
                  command=self.delete_order).grid(row=0, column=4, padx=5)

        self.load_orders()

    def fetch_by_order(self, order_id):
        return session.query(OrderItem).filter_by(order_id=order_id).all()

    def load_orders(self):
        for row in self.table.get_children():
            self.table.delete(row)

        om = self.controller.order_manager
        cm = self.controller.client_manager
        oim = self.controller.order_item_manager

        for order in om.fetch_all():
            client = cm.fetch_by_id(order.client_id)
            items = oim.fetch_by_order(order.order_id)
            item_count = sum(i.quantity for i in items)

            self.table.insert("", "end", values=(
                order.order_id,
                client.client_name if client else "Unknown",
                order.order_status,
                item_count
            ))

    def get_selected_order_id(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select an order first")
            return None
        values = self.table.item(selected[0], "values")
        return int(values[0])

    def create_order_popup(self):
        CreateOrderWindow(self, self.controller)

    def add_item_popup(self):
        order_id = self.get_selected_order_id()
        if order_id is None:
            return
        AddItemWindow(self, self.controller, order_id)

    def commit_selected_order(self):
        order_id = self.get_selected_order_id()
        if order_id is None:
            return
        om = self.controller.order_manager
        om.commit_order(order_id)
        self.load_orders()
        messagebox.showinfo("Committed", f"Order #{order_id} committed")

    def create_shipment_popup(self):
        order_id = self.get_selected_order_id()
        if order_id is None:
            return
        CreateShipmentWindow(self, self.controller, order_id)

    def show_order_items(self, event):
        selected = self.table.selection()
        if not selected:
            return

        values = self.table.item(selected[0], "values")
        order_id = int(values[0])

        OrderItemsWindow(self, self.controller, order_id)

    def delete_order(self):
        order_id = self.get_selected_order_id()
        if order_id is None:
            return

        if not messagebox.askyesno("Confirm Delete", f"Delete Order #{order_id}?"):
            return

        om = self.controller.order_manager
        oim = self.controller.order_item_manager
        sm = self.controller.shipment_manager

        # Delete order items
        items = oim.fetch_by_order(order_id)
        for item in items:
            oim.delete(item.order_item_id)

        # Delete shipment if exists
        shipment = sm.fetch_by_id(order_id)
        if shipment:
            sm.delete(shipment.shipment_id)

        # Delete the order
        om.delete(order_id)

        self.load_orders()
        messagebox.showinfo("Deleted", f"Order #{order_id} deleted")

class OrderItemsWindow(tk.Toplevel):
    def __init__(self, parent, controller, order_id):
        super().__init__(parent)
        self.controller = controller
        self.order_id = order_id

        self.title(f"Order #{order_id} Items")
        self.geometry("600x400")
        self.configure(bg=CONTENT_BG)

        tk.Label(self, text=f"Items in Order #{order_id}",
                 font=("Segoe UI", 16), bg=CONTENT_BG).pack(pady=10)

        columns = ("Product", "SKU", "Quantity", "Location", "Remaining Stock")
        table = ttk.Treeview(self, columns=columns, show="headings", height=12)

        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=120, anchor="center")

        table.pack(pady=10, fill="both", expand=True)

        pm = controller.product_manager
        sm = controller.stock_manager
        oim = controller.order_item_manager

        items = oim.fetch_by_order(order_id)

        for item in items:
            product = pm.fetch_by_id(item.product_id)
            if not product:
                continue

            remaining = sm.stock_level(item.product_id)
            location = ", ".join([s.location for s in product.stock]) or "Unknown"

            table.insert("", "end", values=(
                product.product_name,
                product.sku,
                item.quantity,
                location,
                remaining
            ))



class ShipmentsScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Shipments")

        center = tk.Frame(self.content, bg=CONTENT_BG)
        center.grid(row=0, column=0)

        columns = ("Shipment ID", "Order ID", "Status")
        self.table = ttk.Treeview(center, columns=columns, show="headings", height=12)

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=180, anchor="center")

        self.table.pack(pady=10)

        # ---------- Buttons ----------
        btn_frame = tk.Frame(center, bg=CONTENT_BG)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Mark Shipped", width=15, bg="#27ae60", fg="white",
                  command=self.mark_shipped).grid(row=0, column=0, padx=5)

        tk.Button(btn_frame, text="Mark Delivered", width=15, bg="#8e44ad", fg="white",
                  command=self.mark_delivered).grid(row=0, column=1, padx=5)

        tk.Button(btn_frame, text="Delete Shipment", width=15, bg="#c0392b", fg="white",
                  command=self.delete_shipment).grid(row=0, column=2, padx=5)

        self.load_shipments()

    def load_shipments(self):
        for row in self.table.get_children():
            self.table.delete(row)

        sm = self.controller.shipment_manager

        for shipment in sm.fetch_all():
            self.table.insert("", "end", values=(
                shipment.shipment_id,
                shipment.order_id,
                shipment.shipment_status
            ))

    def get_selected_shipment_id(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a shipment first")
            return None
        values = self.table.item(selected[0], "values")
        return int(values[0])

    def mark_shipped(self):
        shipment_id = self.get_selected_shipment_id()
        if shipment_id is None:
            return
        sm = self.controller.shipment_manager
        sm.mark_as_shipped(shipment_id)
        self.load_shipments()
        messagebox.showinfo("Updated", f"Shipment #{shipment_id} marked as shipped")

    def mark_delivered(self):
        shipment_id = self.get_selected_shipment_id()
        if shipment_id is None:
            return
        sm = self.controller.shipment_manager
        sm.mark_as_delivered(shipment_id)
        self.load_shipments()
        messagebox.showinfo("Updated", f"Shipment #{shipment_id} marked as delivered")

    def delete_shipment(self):
        shipment_id = self.get_selected_shipment_id()
        if shipment_id is None:
            return

        if not messagebox.askyesno("Confirm Delete", f"Delete Shipment #{shipment_id}?"):
            return

        sm = self.controller.shipment_manager
        sm.delete(shipment_id)

        self.load_shipments()
        messagebox.showinfo("Deleted", f"Shipment #{shipment_id} deleted")


class ReportsScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Reports")

        center = tk.Frame(self.content, bg=CONTENT_BG)
        center.grid(row=0, column=0)

        tk.Label(center, text="Reports & Analytics", font=("Segoe UI", 14), bg=CONTENT_BG).pack(pady=10)

        tk.Button(center, text="Inventory Report", width=25, bg=ACCENT, fg="white",
                  command=lambda: InventoryReportWindow(controller)).pack(pady=5)

        tk.Button(center, text="Low Stock Report", width=25, bg="#e67e22", fg="white",
                  command=lambda: LowStockReportWindow(controller)).pack(pady=5)


# ---------- Run app ----------

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()
