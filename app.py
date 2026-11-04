import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import random
import io

if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

try:
    import qrcode
    from PIL import Image, ImageTk
    HAS_QR = True
except ImportError:
    HAS_QR = False


class SupermarketBillingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Supermarket Billing System - Automated Reorder Logic")
        self.root.geometry("1250x720")
        self.root.minsize(1050, 650)
        self.root.configure(bg="#1a1a2e")

        self.stock = {'rice': 40, 'milk': 6, 'eggs': 12, 'bread': 3, 'sugar': 18}
        self.rpoint = {'rice': 30, 'milk': 10, 'eggs': 20, 'bread': 5, 'sugar': 15}
        self.prices = {'rice': 60.0, 'milk': 32.0, 'eggs': 75.0, 'bread': 40.0, 'sugar': 44.0}
        self.units = {'rice': 'kg', 'milk': 'L', 'eggs': 'doz', 'bread': 'pk', 'sugar': 'kg'}

        self.cart = {}
        self.invoice_number = f"INV-{random.randint(10000, 99999)}"
        self.payment_mode = tk.StringVar(value="Cash")
        self.current_subtotal = 0.0
        self.current_discount = 0.0
        self.current_tax = 0.0
        self.current_grand_total = 0.0

        self.BG = "#1a1a2e"
        self.CARD = "#16213e"
        self.ACCENT = "#0f3460"
        self.TEXT = "#e8e8e8"
        self.MUTED = "#8d99ae"
        self.GREEN = "#2ecc71"
        self.RED = "#e74c3c"
        self.BLUE = "#3498db"

        self._setup_styles()
        self._build_ui()
        self.on_product_selected()
        self._refresh_inventory()
        self._update_clock()

    def needs_reorder(self, item):
        return self.stock.get(item, 0) < self.rpoint.get(item, 0)

    def get_reorder_alerts(self):
        return [item for item in self.stock if self.needs_reorder(item)]

    def _setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Treeview",
            background=self.CARD, foreground=self.TEXT,
            fieldbackground=self.CARD, rowheight=28,
            font=("Segoe UI", 9))
        self.style.configure("Treeview.Heading",
            background=self.ACCENT, foreground=self.TEXT,
            font=("Segoe UI", 9, "bold"))
        self.style.map("Treeview",
            background=[('selected', self.BLUE)],
            foreground=[('selected', '#ffffff')])

    def _build_ui(self):
        header = tk.Frame(self.root, bg=self.ACCENT, height=55)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="🛒 SUPERMARKET BILLING SYSTEM",
                 font=("Segoe UI", 14, "bold"), bg=self.ACCENT, fg="#fff"
                 ).pack(side=tk.LEFT, padx=15, pady=10)
        tk.Label(header,
                 text="Rule: needs_reorder(X) ← stock(X) < threshold(X)",
                 font=("Consolas", 9), bg=self.ACCENT, fg="#8db8d8"
                 ).pack(side=tk.LEFT, padx=15)
        self.clock_lbl = tk.Label(header, text="", font=("Segoe UI", 9),
                                  bg=self.ACCENT, fg="#bbb")
        self.clock_lbl.pack(side=tk.RIGHT, padx=15)

        main = tk.Frame(self.root, bg=self.BG)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        left = tk.Frame(main, bg=self.BG)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        right = tk.Frame(main, bg=self.BG, width=420)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right.pack_propagate(False)

        self._build_customer_section(left)
        self._build_product_section(left)
        self._build_cart_section(left)
        self._build_checkout_section(left)
        self._build_inventory_section(right)
        self._build_receipt_section(right)

    def _build_customer_section(self, parent):
        f = tk.LabelFrame(parent, text=" Customer Info ",
                          bg=self.CARD, fg=self.TEXT,
                          font=("Segoe UI", 9, "bold"), padx=8, pady=5)
        f.pack(fill=tk.X, pady=(0, 6))

        tk.Label(f, text="Name:", bg=self.CARD, fg=self.MUTED,
                 font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
        self.cust_name = tk.StringVar(value="Walk-in Customer")
        tk.Entry(f, textvariable=self.cust_name, width=18,
                 font=("Segoe UI", 9), bg=self.ACCENT, fg="#fff",
                 insertbackground="#fff").grid(row=0, column=1, padx=5)

        tk.Label(f, text="Phone:", bg=self.CARD, fg=self.MUTED,
                 font=("Segoe UI", 9)).grid(row=0, column=2, padx=(10, 0))
        self.cust_phone = tk.StringVar(value="+91 98765-43210")
        tk.Entry(f, textvariable=self.cust_phone, width=14,
                 font=("Segoe UI", 9), bg=self.ACCENT, fg="#fff",
                 insertbackground="#fff").grid(row=0, column=3, padx=5)

        tk.Label(f, text="Invoice:", bg=self.CARD, fg=self.MUTED,
                 font=("Segoe UI", 9)).grid(row=0, column=4, padx=(10, 0))
        self.inv_lbl = tk.Label(f, text=self.invoice_number,
                                font=("Segoe UI", 9, "bold"),
                                bg=self.CARD, fg=self.GREEN)
        self.inv_lbl.grid(row=0, column=5, padx=5)

    def _build_product_section(self, parent):
        f = tk.LabelFrame(parent, text=" Product Selection ",
                          bg=self.CARD, fg=self.TEXT,
                          font=("Segoe UI", 9, "bold"), padx=8, pady=5)
        f.pack(fill=tk.X, pady=(0, 6))

        tk.Label(f, text="Item:", bg=self.CARD, fg=self.MUTED,
                 font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
        self.selected_item = tk.StringVar(value="rice")
        self.item_combo = ttk.Combobox(f, textvariable=self.selected_item,
                                       values=list(self.stock.keys()),
                                       state="readonly", width=12,
                                       font=("Segoe UI", 9))
        self.item_combo.grid(row=0, column=1, padx=5)
        self.item_combo.bind("<<ComboboxSelected>>", self.on_product_selected)

        tk.Label(f, text="Price:", bg=self.CARD, fg=self.MUTED,
                 font=("Segoe UI", 9)).grid(row=0, column=2, padx=(10, 0))
        self.price_lbl = tk.StringVar()
        tk.Label(f, textvariable=self.price_lbl, bg=self.CARD, fg=self.GREEN,
                 font=("Segoe UI", 9, "bold")).grid(row=0, column=3)

        tk.Label(f, text="Stock:", bg=self.CARD, fg=self.MUTED,
                 font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", pady=4)
        self.stock_lbl = tk.StringVar()
        tk.Label(f, textvariable=self.stock_lbl, bg=self.CARD, fg=self.BLUE,
                 font=("Segoe UI", 9, "bold")).grid(row=1, column=1)

        tk.Label(f, text="Threshold:", bg=self.CARD, fg=self.MUTED,
                 font=("Segoe UI", 9)).grid(row=1, column=2, padx=(10, 0))
        self.thresh_lbl = tk.StringVar()
        tk.Label(f, textvariable=self.thresh_lbl, bg=self.CARD, fg=self.TEXT,
                 font=("Segoe UI", 9)).grid(row=1, column=3)

        self.status_lbl = tk.Label(f, text="", font=("Segoe UI", 8, "bold"),
                                   padx=6, pady=2)
        self.status_lbl.grid(row=1, column=4, columnspan=2, padx=10)

        tk.Label(f, text="Qty:", bg=self.CARD, fg=self.MUTED,
                 font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w", pady=4)
        self.qty_var = tk.IntVar(value=1)
        qty_spin = tk.Spinbox(f, from_=1, to=999, textvariable=self.qty_var,
                              width=5, font=("Segoe UI", 9),
                              bg=self.ACCENT, fg="#fff")
        qty_spin.grid(row=2, column=1, padx=5)
        qty_spin.bind("<Return>", lambda e: self.add_to_cart())

        tk.Button(f, text="Add to Cart", font=("Segoe UI", 9, "bold"),
                  bg=self.BLUE, fg="#fff", relief="flat", padx=8,
                  command=self.add_to_cart).grid(row=2, column=2, columnspan=2, padx=5)

        tk.Button(f, text="Remove Selected", font=("Segoe UI", 9),
                  bg=self.RED, fg="#fff", relief="flat", padx=8,
                  command=self.remove_from_cart).grid(row=2, column=4, padx=5)

    def _build_cart_section(self, parent):
        f = tk.LabelFrame(parent, text=" Shopping Cart ",
                          bg=self.CARD, fg=self.TEXT,
                          font=("Segoe UI", 9, "bold"), padx=8, pady=5)
        f.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        cols = ("item", "price", "qty", "total")
        self.cart_tree = ttk.Treeview(f, columns=cols, show="headings", height=5)
        self.cart_tree.heading("item", text="Item")
        self.cart_tree.heading("price", text="Unit Price")
        self.cart_tree.heading("qty", text="Quantity")
        self.cart_tree.heading("total", text="Subtotal")
        self.cart_tree.column("item", width=120)
        self.cart_tree.column("price", width=90, anchor="center")
        self.cart_tree.column("qty", width=80, anchor="center")
        self.cart_tree.column("total", width=90, anchor="e")

        sb = ttk.Scrollbar(f, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=sb.set)
        self.cart_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.cart_tree.bind("<Delete>", lambda e: self.remove_from_cart())

    def _build_checkout_section(self, parent):
        f = tk.LabelFrame(parent, text=" Billing Summary & Payment ",
                          bg=self.CARD, fg=self.TEXT,
                          font=("Segoe UI", 9, "bold"), padx=10, pady=6)
        f.pack(fill=tk.X)

        left = tk.Frame(f, bg=self.CARD)
        left.pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(left, text="Subtotal:", bg=self.CARD, fg=self.MUTED,
                 font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
        self.subtotal_var = tk.StringVar(value="₹0.00")
        tk.Label(left, textvariable=self.subtotal_var, bg=self.CARD,
                 fg=self.TEXT, font=("Segoe UI", 9, "bold")
                 ).grid(row=0, column=1, padx=8, sticky="e")

        tk.Label(left, text="Discount %:", bg=self.CARD, fg=self.MUTED,
                 font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w")
        self.discount_var = tk.DoubleVar(value=0.0)
        disc_spin = tk.Spinbox(left, from_=0, to=50, increment=5,
                               textvariable=self.discount_var, width=4,
                               font=("Segoe UI", 9), bg=self.ACCENT, fg="#fff",
                               command=self.recalculate)
        disc_spin.grid(row=1, column=1, sticky="e", padx=8)
        disc_spin.bind("<KeyRelease>", lambda e: self.recalculate())

        tk.Label(left, text="Tax (5% GST):", bg=self.CARD, fg=self.MUTED,
                 font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w")
        self.tax_var = tk.StringVar(value="₹0.00")
        tk.Label(left, textvariable=self.tax_var, bg=self.CARD,
                 fg=self.TEXT, font=("Segoe UI", 9)
                 ).grid(row=2, column=1, padx=8, sticky="e")

        tk.Label(left, text="GRAND TOTAL:", bg=self.CARD, fg=self.GREEN,
                 font=("Segoe UI", 10, "bold")
                 ).grid(row=3, column=0, sticky="w", pady=4)
        self.total_var = tk.StringVar(value="₹0.00")
        tk.Label(left, textvariable=self.total_var, bg=self.CARD,
                 fg=self.GREEN, font=("Segoe UI", 12, "bold")
                 ).grid(row=3, column=1, padx=8, sticky="e")

        mid = tk.Frame(f, bg=self.CARD)
        mid.pack(side=tk.LEFT, padx=15)

        tk.Label(mid, text="Payment Mode:", bg=self.CARD, fg=self.MUTED,
                 font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
        modes_combo = ttk.Combobox(mid, textvariable=self.payment_mode,
                                   values=["Cash", "Card", "UPI"],
                                   state="readonly", width=8,
                                   font=("Segoe UI", 9))
        modes_combo.grid(row=0, column=1, padx=5)

        tk.Label(mid, text="Cash Given:", bg=self.CARD, fg=self.MUTED,
                 font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", pady=3)
        self.cash_var = tk.DoubleVar(value=0.0)
        cash_entry = tk.Entry(mid, textvariable=self.cash_var, width=8,
                              font=("Segoe UI", 9, "bold"), bg=self.ACCENT,
                              fg="#fff", insertbackground="#fff")
        cash_entry.grid(row=1, column=1, padx=5)
        cash_entry.bind("<KeyRelease>", self.calc_change)

        tk.Label(mid, text="Change:", bg=self.CARD, fg=self.MUTED,
                 font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w")
        self.change_var = tk.StringVar(value="₹0.00")
        self.change_lbl = tk.Label(mid, textvariable=self.change_var,
                                   bg=self.CARD, fg=self.BLUE,
                                   font=("Segoe UI", 10, "bold"))
        self.change_lbl.grid(row=2, column=1, padx=5, sticky="e")

        btn_frame = tk.Frame(f, bg=self.CARD)
        btn_frame.pack(side=tk.RIGHT, padx=5)

        tk.Button(btn_frame, text="Finalize Bill", width=16,
                  font=("Segoe UI", 10, "bold"), bg=self.GREEN, fg="#fff",
                  relief="flat", pady=6,
                  command=self.generate_bill).pack(pady=2)
        tk.Button(btn_frame, text="Clear Cart", width=16,
                  font=("Segoe UI", 9), bg=self.RED, fg="#fff",
                  relief="flat", pady=4,
                  command=self.clear_cart).pack(pady=2)

    def _build_inventory_section(self, parent):
        f = tk.LabelFrame(parent, text=" Inventory & Reorder Monitor ",
                          bg=self.CARD, fg=self.TEXT,
                          font=("Segoe UI", 9, "bold"), padx=8, pady=5)
        f.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        tk.Label(f, text="Rule: needs_reorder(X) ← stock(X) < rpoint(X)",
                 font=("Consolas", 8), bg=self.BG, fg=self.MUTED,
                 padx=5, pady=3).pack(fill=tk.X, pady=(0, 4))

        cols = ("item", "stock", "threshold", "status")
        self.inv_tree = ttk.Treeview(f, columns=cols, show="headings", height=5)
        self.inv_tree.heading("item", text="Product")
        self.inv_tree.heading("stock", text="Stock")
        self.inv_tree.heading("threshold", text="Threshold")
        self.inv_tree.heading("status", text="Status")
        self.inv_tree.column("item", width=80)
        self.inv_tree.column("stock", width=60, anchor="center")
        self.inv_tree.column("threshold", width=70, anchor="center")
        self.inv_tree.column("status", width=120, anchor="center")
        self.inv_tree.tag_configure("ok", foreground="#2ecc71")
        self.inv_tree.tag_configure("reorder", foreground="#e74c3c",
                                    background="#3d1515")
        self.inv_tree.pack(fill=tk.BOTH, expand=True)

        btn_box = tk.Frame(f, bg=self.CARD)
        btn_box.pack(fill=tk.X, pady=(5, 0))

        tk.Button(btn_box, text="Restock (+20)",
                  font=("Segoe UI", 9, "bold"), bg=self.BLUE, fg="#fff",
                  relief="flat",
                  command=self.restock_selected).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))

        tk.Button(btn_box, text="Add New Item",
                  font=("Segoe UI", 9, "bold"), bg=self.GREEN, fg="#fff",
                  relief="flat",
                  command=self.add_new_product_window).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))

    def _build_receipt_section(self, parent):
        f = tk.LabelFrame(parent, text=" Receipt Preview ",
                          bg=self.CARD, fg=self.TEXT,
                          font=("Segoe UI", 9, "bold"), padx=8, pady=5)
        f.pack(fill=tk.BOTH, expand=True)

        self.receipt_text = tk.Text(f, font=("Consolas", 8), bg="#f5f5f5",
                                   fg="#222", relief="flat", wrap="word",
                                   padx=8, pady=6)
        self.receipt_text.pack(fill=tk.BOTH, expand=True)
        self._set_default_receipt()

        tk.Button(f, text="Save Receipt", font=("Segoe UI", 9, "bold"),
                  bg=self.BLUE, fg="#fff", relief="flat",
                  command=self.save_receipt).pack(fill=tk.X, pady=(4, 0))

    def _set_default_receipt(self):
        self.receipt_text.config(state="normal")
        self.receipt_text.delete("1.0", tk.END)
        self.receipt_text.insert(tk.END,
            "== RECEIPT PREVIEW ==\n\n"
            "Add items to cart and click\n"
            "'Finalize Bill' to generate receipt.")
        self.receipt_text.config(state="disabled")

    def on_product_selected(self, event=None):
        item = self.selected_item.get()
        if item not in self.stock:
            return
        unit = self.units[item]
        self.price_lbl.set(f"₹{self.prices[item]:.2f}/{unit}")
        self.stock_lbl.set(f"{self.stock[item]} {unit}")
        self.thresh_lbl.set(f"{self.rpoint[item]} {unit}")

        if self.needs_reorder(item):
            self.status_lbl.config(text="⚠ REORDER NEEDED",
                                   bg=self.RED, fg="#fff")
        else:
            self.status_lbl.config(text="✓ In Stock",
                                   bg=self.GREEN, fg="#fff")

    def add_to_cart(self):
        item = self.selected_item.get()
        try:
            qty = int(self.qty_var.get())
            if qty <= 0:
                raise ValueError
        except (ValueError, tk.TclError):
            messagebox.showerror("Error", "Enter a valid quantity.")
            return

        in_cart = self.cart.get(item, {}).get('qty', 0)
        if qty + in_cart > self.stock[item]:
            messagebox.showwarning("Insufficient Stock",
                f"Only {self.stock[item]} available, "
                f"{in_cart} already in cart.")
            return

        new_qty = in_cart + qty
        price = self.prices[item]
        self.cart[item] = {
            'price': price, 'qty': new_qty,
            'total': new_qty * price, 'unit': self.units[item]
        }
        self._refresh_cart()
        self.recalculate()

    def remove_from_cart(self):
        sel = self.cart_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select an item to remove.")
            return
        name = str(self.cart_tree.item(sel[0])['values'][0]).lower()
        if name in self.cart:
            del self.cart[name]
            self._refresh_cart()
            self.recalculate()

    def clear_cart(self):
        if not self.cart:
            return
        if messagebox.askyesno("Clear", "Clear the entire cart?"):
            self.cart.clear()
            self.invoice_number = f"INV-{random.randint(10000, 99999)}"
            self.inv_lbl.config(text=self.invoice_number)
            self._refresh_cart()
            self.recalculate()

    def _refresh_cart(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)
        for item, d in self.cart.items():
            self.cart_tree.insert("", tk.END, values=(
                item.title(), f"₹{d['price']:.2f}",
                f"{d['qty']} {d['unit']}", f"₹{d['total']:.2f}"))

    def recalculate(self):
        subtotal = sum(d['total'] for d in self.cart.values())
        try:
            disc_pct = float(self.discount_var.get())
        except (ValueError, tk.TclError):
            disc_pct = 0.0
        discount = subtotal * disc_pct / 100
        taxable = max(0, subtotal - discount)
        tax = taxable * 0.05
        total = taxable + tax

        self.current_subtotal = subtotal
        self.current_discount = discount
        self.current_tax = tax
        self.current_grand_total = total

        self.subtotal_var.set(f"₹{subtotal:.2f}")
        self.tax_var.set(f"₹{tax:.2f}")
        self.total_var.set(f"₹{total:.2f}")
        self.calc_change()

    def calc_change(self, event=None):
        try:
            cash = float(self.cash_var.get())
            change = cash - self.current_grand_total
            if change >= 0:
                self.change_var.set(f"₹{change:.2f}")
                self.change_lbl.config(fg=self.GREEN)
            else:
                self.change_var.set(f"-₹{abs(change):.2f}")
                self.change_lbl.config(fg=self.RED)
        except (ValueError, tk.TclError):
            self.change_var.set("₹0.00")

    def generate_bill(self):
        if not self.cart:
            messagebox.showwarning("Empty", "Cart is empty!")
            return

        for item, d in self.cart.items():
            self.stock[item] -= d['qty']

        reorder_list = self.get_reorder_alerts()

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        name = self.cust_name.get() or "Customer"
        phone = self.cust_phone.get() or "N/A"
        mode = self.payment_mode.get()

        lines = [
            "=" * 40,
            "      SMART SUPERMARKET BILLING",
            "     Connaught Place, New Delhi",
            "=" * 40,
            f"Invoice : {self.invoice_number}",
            f"Date    : {now}",
            f"Customer: {name}",
            f"Phone   : {phone}",
            f"Payment : {mode}",
            "-" * 40,
            f"{'Item':<12} {'Qty':<8} {'Price':<8} {'Total':>8}",
            "-" * 40,
        ]
        for item, d in self.cart.items():
            lines.append(
                f"{item.title():<12} {d['qty']}{d['unit']:<7} "
                f"₹{d['price']:<7.1f} ₹{d['total']:>7.2f}")
        lines.append("-" * 40)
        lines.append(f"{'Subtotal:':<30} ₹{self.current_subtotal:>8.2f}")
        if self.current_discount > 0:
            lines.append(
                f"{'Discount:':<30} -₹{self.current_discount:>7.2f}")
        lines.append(f"{'Tax (5% GST):':<30} ₹{self.current_tax:>8.2f}")
        lines.append("=" * 40)
        lines.append(
            f"{'GRAND TOTAL:':<30} ₹{self.current_grand_total:>8.2f}")
        lines.append(
            f"{'Paid ({mode}):':<30} ₹{self.cash_var.get():>8.2f}")
        lines.append(
            f"{'Change:':<30} {self.change_var.get():>9}")
        lines.append("=" * 40)

        lines.append("  AUTOMATED REORDER STATUS:")
        if reorder_list:
            for itm in reorder_list:
                lines.append(
                    f"  ⚠ {itm.upper()}: Stock={self.stock[itm]}"
                    f" < Threshold={self.rpoint[itm]}")
        else:
            lines.append("  ✓ All items have sufficient stock")
        lines.append("=" * 40)
        lines.append("      Thank you for shopping!")

        receipt = "\n".join(lines)

        self.receipt_text.config(state="normal")
        self.receipt_text.delete("1.0", tk.END)
        self.receipt_text.insert(tk.END, receipt)
        self.receipt_text.config(state="disabled")

        self._refresh_inventory()
        self.on_product_selected()

        if mode == "UPI":
            self._show_upi_qr()

        if reorder_list:
            items_str = "\n".join(
                f"• {it.upper()}: Stock={self.stock[it]} "
                f"(Threshold={self.rpoint[it]})"
                for it in reorder_list)
            messagebox.showwarning("Reorder Alert",
                f"Bill generated!\n\n"
                f"Rule: needs_reorder(X) ← stock < threshold\n\n"
                f"Items needing restock:\n{items_str}")
        else:
            messagebox.showinfo("Success", "Bill finalized successfully!")

        self.cart.clear()
        self.invoice_number = f"INV-{random.randint(10000, 99999)}"
        self.inv_lbl.config(text=self.invoice_number)
        self._refresh_cart()
        self.recalculate()

    def _show_upi_qr(self):
        if not HAS_QR:
            messagebox.showinfo("QR Code",
                "QR code feature requires 'qrcode' and 'pillow' packages.\n"
                "Install them with: pip install qrcode pillow")
            return

        amount = self.current_grand_total
        upi_id = "9204252121@pthdfc"
        store_name = "Ansh Raj"

        upi_string = (
            f"upi://pay?pa={upi_id}&pn={store_name}"
            f"&am={amount:.2f}&cu=INR"
            f"&tn=Invoice_{self.invoice_number}")

        qr = qrcode.QRCode(version=1, box_size=6, border=2,
                            error_correction=qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(upi_string)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        pil_img = Image.open(img_bytes)
        tk_img = ImageTk.PhotoImage(pil_img)

        qr_win = tk.Toplevel(self.root)
        qr_win.title("UPI Payment QR Code")
        qr_win.configure(bg="#ffffff")
        qr_win.resizable(False, False)

        tk.Label(qr_win, text="Scan to Pay via UPI",
                 font=("Segoe UI", 12, "bold"),
                 bg="#fff", fg="#333").pack(pady=(15, 5))

        tk.Label(qr_win, text=f"Amount: ₹{amount:.2f}",
                 font=("Segoe UI", 11, "bold"),
                 bg="#fff", fg="#2ecc71").pack()

        img_label = tk.Label(qr_win, image=tk_img, bg="#fff")
        img_label.image = tk_img
        img_label.pack(padx=25, pady=10)

        tk.Label(qr_win, text=f"UPI ID: {upi_id}",
                 font=("Segoe UI", 9), bg="#fff", fg="#666").pack()
        tk.Label(qr_win, text=f"Invoice: {self.invoice_number}",
                 font=("Segoe UI", 9), bg="#fff", fg="#666").pack(pady=(0, 5))

        tk.Button(qr_win, text="Close", font=("Segoe UI", 9, "bold"),
                  bg="#3498db", fg="#fff", relief="flat", padx=20, pady=4,
                  command=qr_win.destroy).pack(pady=(5, 15))

    def _refresh_inventory(self):
        for row in self.inv_tree.get_children():
            self.inv_tree.delete(row)
        for item in self.stock:
            qty = self.stock[item]
            thresh = self.rpoint[item]
            unit = self.units[item]
            reorder = self.needs_reorder(item)
            status = "⚠ REORDER" if reorder else "✓ In Stock"
            tag = "reorder" if reorder else "ok"
            self.inv_tree.insert("", tk.END,
                values=(item.title(), f"{qty} {unit}",
                        f"{thresh} {unit}", status),
                tags=(tag,))

    def restock_selected(self):
        sel = self.inv_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a product to restock.")
            return
        item = str(self.inv_tree.item(sel[0])['values'][0]).lower()
        if item in self.stock:
            self.stock[item] += 20
            self._refresh_inventory()
            self.on_product_selected()
            messagebox.showinfo("Restocked",
                f"+20 added to '{item.title()}'.\n"
                f"New stock: {self.stock[item]}")

    def add_new_product_window(self):
        win = tk.Toplevel(self.root)
        win.title("Add New Product")
        win.geometry("320x290")
        win.configure(bg=self.CARD)
        win.resizable(False, False)

        tk.Label(win, text="Add New Inventory Product", font=("Segoe UI", 11, "bold"),
                 bg=self.CARD, fg="#fff").pack(pady=(12, 10))

        form = tk.Frame(win, bg=self.CARD)
        form.pack(padx=20, fill=tk.X)

        fields = [
            ("Item Name:", "name"),
            ("Price (₹):", "price"),
            ("Current Stock:", "stock"),
            ("Reorder Threshold:", "thresh"),
            ("Unit (kg/L/pk/etc):", "unit")
        ]
        entries = {}
        for idx, (label, key) in enumerate(fields):
            tk.Label(form, text=label, font=("Segoe UI", 9), bg=self.CARD, fg=self.MUTED).grid(row=idx, column=0, sticky="w", pady=3)
            e = tk.Entry(form, font=("Segoe UI", 9), bg=self.ACCENT, fg="#fff", insertbackground="#fff", width=14)
            e.grid(row=idx, column=1, padx=(10, 0), pady=3)
            entries[key] = e

        entries["unit"].insert(0, "pk")

        def save():
            name = entries["name"].get().strip().lower()
            if not name:
                messagebox.showerror("Error", "Enter a valid product name.", parent=win)
                return
            if name in self.stock:
                messagebox.showerror("Error", "Product already exists.", parent=win)
                return
            try:
                price = float(entries["price"].get())
                stock = int(entries["stock"].get())
                thresh = int(entries["thresh"].get())
                unit = entries["unit"].get().strip() or "unit"
                if price <= 0 or stock < 0 or thresh < 0:
                    raise ValueError
            except (ValueError, tk.TclError):
                messagebox.showerror("Error", "Enter valid numeric values for price, stock, and threshold.", parent=win)
                return

            self.stock[name] = stock
            self.rpoint[name] = thresh
            self.prices[name] = price
            self.units[name] = unit

            self.item_combo['values'] = list(self.stock.keys())
            self.selected_item.set(name)
            self.on_product_selected()
            self._refresh_inventory()

            win.destroy()
            messagebox.showinfo("Success", f"Product '{name.title()}' added successfully!")

        tk.Button(win, text="Save Product", font=("Segoe UI", 9, "bold"),
                  bg=self.GREEN, fg="#fff", relief="flat", padx=15, pady=4,
                  command=save).pack(pady=15)

    def save_receipt(self):
        content = self.receipt_text.get("1.0", tk.END).strip()
        if not content or "RECEIPT PREVIEW" in content:
            messagebox.showwarning("No Receipt", "Generate a bill first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            initialfile=f"{self.invoice_number}.txt")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Saved", f"Receipt saved to:\n{path}")

    def _update_clock(self):
        now = datetime.datetime.now().strftime("%a %b %d, %Y  %I:%M:%S %p")
        self.clock_lbl.config(text=now)
        self.root.after(1000, self._update_clock)


if __name__ == "__main__":
    root = tk.Tk()
    app = SupermarketBillingApp(root)
    root.mainloop()
