# 🛒 E-Commerce Website (Django + Bootstrap)

A fully functional **online shopping platform** built using **Django (Python)** for the backend and **HTML, SCSS, Bootstrap 5, jQuery** for the frontend.

---

## 🚀 Features

### 👤 User Features

* User registration & login (OTP verification)
* Password reset & forgot password
* Browse products by categories (Men, Women, Casual)
* Product details with variants & reviews
* Add to cart & wishlist
* Address management
* Checkout with multiple payment options (including Razorpay)
* Wallet system
* Order history & tracking

---

### 🛠️ Admin Dashboard

* Product, variant, category & sub-category management
* Banner, coupon & offer management
* User management (block/unblock)
* Order management
* Sales reports with interactive charts (ApexCharts)
* Top-selling products & categories analytics

---

## 🧰 Tech Stack

| Layer    | Technology                       |
| -------- | -------------------------------- |
| Backend  | Django (Python)                  |
| Frontend | HTML5, SCSS, Bootstrap 5 |
| Charts   | ApexCharts                       |
| Styling  | Bootstrap,css                    |
| Icons    | IonIcons, Flaticon               |
| Payments | Razorpay                         |
| Database | PostgreSQL                       |

---

## ⚙️ Installation & Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/your-ecommerce-project.git
cd your-ecommerce-project

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# Install dependencies
pip install django pillow

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

---

## 📁 Project Structure

```
├── template/
│   ├── admin/
│   └── user/
├── static/
│   ├── css/
│   ├── js/
│   └── img/
├── user/
├── user_app/
├── wishlist/
├── assets/
└── manage.py
```

---

## 🔑 Key Highlights

* Secure authentication with OTP verification
* AJAX-based coupon application
* Dynamic cart & checkout flow
* Address validation before checkout
* Razorpay payment integration
* Admin analytics dashboard with charts

---

## 📌 Future Improvements

* Add REST API (Django REST Framework)
* Add product search & filters
* Improve UI/UX animations
* Add unit & integration tests

---

## 👨‍💻 Author

**Midhun G**

