# Supermarket Billing System - Automated Reorder Logic

A desktop billing and inventory management application built using Python (Tkinter).

## Features
- **Product Billing & Cart**: Add products, adjust quantities, calculate discounts, tax (5% GST), and totals.
- **Automated Reorder Logic**: Triggers alerts when stock falls below threshold levels (`stock < threshold`).
- **Inventory Monitor**: Live view of stock and thresholds with manual restock capabilities.
- **Add Custom Products**: Add new inventory items on the fly with custom price, threshold, and unit.
- **UPI QR Code Generation**: Generates scannable UPI payment QR codes on checkout.
- **Receipt Generation**: Printable text receipt exportable directly to `.txt`.

## Requirements
- Python 3.8+
- Required libraries for UPI QR code:
  ```bash
  pip install qrcode pillow
  ```

## Running the Application
```bash
python app.py
```
