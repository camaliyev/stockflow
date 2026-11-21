# StockFlow

A Django inventory and order management application with customer carts, staff controls, and stock movement history.

## Features

### Customers
- Log in and browse active products with available stock.
- Search products by name or SKU and filter by category.
- Create a draft order that acts as a cart.
- Add products, edit quantities, and remove items before confirmation.
- Confirm an order and view its total.
- View only their own orders.
- Confirmed orders become read-only for customers.

### Staff
- View all products and orders.
- Create and edit products.
- Adjust stock with a recorded reason.
- View stock movement history and who recorded each change.
- Edit quantities on confirmed orders with automatic stock adjustment.
- Cancel orders, returning stock when the order was confirmed.

## Order and Stock Rules

- Draft orders do not reserve or reduce stock.
- Confirmation checks product availability and deducts stock.
- Changing a confirmed item's quantity adjusts stock by the difference.
- Cancelling a confirmed order restores its current item quantities.
- Cancelling a draft order does not change stock.
- Cancelled orders cannot be edited.
- Item prices are copied from the product when added to an order.
- Database transactions keep related order and stock changes together.

## Technology

- Python
- Django
- SQLite for local development
- Django templates
- HTML and CSS
- Django's built-in authentication

## Project Structure

- `config/` — project settings and main URL configuration.
- `inventory/` — products, categories, and stock movements.
- `orders/` — carts, order items, order workflows, and access rules.
- `templates/` — shared page layout.
- `static/` — shared styles.

Business operations live in service functions, while views handle requests, forms, and responses.

## Local Setup

Clone this repository and open its directory.

### 1. Create and activate a virtual environment

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

Use a Python version compatible with the Django version pinned in `requirements.txt`.

### 3. Apply migrations

```bash
python manage.py migrate
```

### 4. Create an administrator

```bash
python manage.py createsuperuser
```

### 5. Start the development server

```bash
python manage.py runserver
```

Open:

- Products: http://127.0.0.1:8000/products/
- Login: http://127.0.0.1:8000/accounts/login/
- Django admin: http://127.0.0.1:8000/admin/

## Demo Walkthrough

1. Sign in as the administrator.
2. Create a category and a product.
3. Use **Adjust stock** to record an opening stock quantity.
4. Create an active customer account through Django admin, leaving staff and superuser status unchecked.
5. Log in as that customer and create a cart.
6. Add products and confirm the order.
7. Log back in as the administrator to review the order and stock history.

Customer accounts are currently created by an administrator; public registration is not included.

## Checks and Tests

```bash
python manage.py check
python manage.py test
```

## Development Notes

This project is intended for local demonstration and learning.

SQLite is used locally. It does not provide row locking through Django's `select_for_update()`. PostgreSQL and additional concurrency testing would be needed to evaluate simultaneous stock updates for production use.

Production deployment also requires environment-based secrets, appropriate host settings, HTTPS, and static-file configuration.