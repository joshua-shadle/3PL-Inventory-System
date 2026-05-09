import tkinter as tk
from fntend import InventoryApp

def test_app_initializes():
    app = InventoryApp()
    assert isinstance(app, tk.Tk)
    app.destroy()

def test_all_screens_exist():
    app = InventoryApp()
    expected = [
        "DashboardScreen",
        "ProductsScreen",
        "ClientsScreen",
        "OrdersScreen",
        "ShipmentsScreen",
        "ReportsScreen",
    ]
    for screen in expected:
        assert screen in app.frames
    app.destroy()

def test_products_screen_widgets():
    app = InventoryApp()
    screen = app.frames["ProductsScreen"]

    assert hasattr(screen, "entries")
    assert len(screen.entries) == 4

    assert hasattr(screen, "table")
    assert screen.table["columns"] == ("Name", "SKU", "Quantity", "Location")

    app.destroy()

def test_reports_buttons_exist():
    app = InventoryApp()
    screen = app.frames["ReportsScreen"]

    # Find all buttons inside the screen
    buttons = [child for child in screen.content.winfo_children()[0].winfo_children() if isinstance(child, tk.Button)]

    labels = [b["text"] for b in buttons]

    assert "Inventory Report" in labels
    assert "Low Stock Report" in labels

    app.destroy()
