import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

def init_db():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      quantity INTEGER NOT NULL,
                      price REAL NOT NULL)''')
    conn.commit()
    conn.close()

def add_product(name, quantity, price):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", (name, quantity, price))
    conn.commit()
    conn.close()

def get_products():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_product(product_id, name, quantity, price):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET name=?, quantity=?, price=? WHERE id=?", (name, quantity, price, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    cursor.execute("VACUUM") 
    conn.close()

def clear_database():
    """Deletes all products and resets ID counter when the program closes."""
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS products") 
    cursor.execute('''CREATE TABLE products (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      quantity INTEGER NOT NULL,
                      price REAL NOT NULL)''')  
    conn.commit()
    conn.close()

def low_stock_alert():
    products = get_products()
    alert_list = [p for p in products if p[2] < 5]  
    if alert_list:
        messagebox.showwarning("Low Stock Alert", "Some items have low stock levels!")

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        tk.Label(root, text="Product Name:").grid(row=0, column=0)
        self.name_entry = tk.Entry(root)
        self.name_entry.grid(row=0, column=1)
        
        tk.Label(root, text="Quantity:").grid(row=1, column=0)
        self.quantity_entry = tk.Entry(root)
        self.quantity_entry.grid(row=1, column=1)
        
        tk.Label(root, text="Price:").grid(row=2, column=0)
        self.price_entry = tk.Entry(root)
        self.price_entry.grid(row=2, column=1)
        
        tk.Button(root, text="Add Product", command=self.add_product).grid(row=3, column=0)
        tk.Button(root, text="Update Product", command=self.update_product).grid(row=3, column=1)
        tk.Button(root, text="Delete Product", command=self.delete_product).grid(row=3, column=2)
        tk.Button(root, text="Refresh", command=self.load_products).grid(row=3, column=3)
        
        self.tree = ttk.Treeview(root, columns=("ID", "Name", "Quantity", "Price"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Quantity", text="Quantity")
        self.tree.heading("Price", text="Price")
        self.tree.grid(row=4, column=0, columnspan=4)
        self.load_products()
        self.auto_refresh()
        
    def add_product(self):
        name = self.name_entry.get()
        quantity = self.quantity_entry.get()
        price = self.price_entry.get()
        if name and quantity.isdigit() and price.replace('.', '', 1).isdigit():
            add_product(name, int(quantity), float(price))
            self.load_products()
        else:
            messagebox.showerror("Error", "Invalid input")

    def update_product(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "No product selected")
            return
        item = self.tree.item(selected)['values']
        product_id = item[0]
        update_product(product_id, self.name_entry.get(), int(self.quantity_entry.get()), float(self.price_entry.get()))
        self.load_products()

    def delete_product(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "No product selected")
            return
        item = self.tree.item(selected)['values']
        delete_product(item[0])
        self.load_products()

    def load_products(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for product in get_products():
            self.tree.insert("", "end", values=product)
        low_stock_alert()

    def auto_refresh(self):
        self.load_products()
        self.root.after(5000, self.auto_refresh)  

    def on_closing(self):
        """Called when the window is closed."""
        if messagebox.askyesno("Exit", "Do you want to clear all data before exiting?"):
            clear_database()
        self.root.destroy()

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
