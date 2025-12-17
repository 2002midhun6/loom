# E-Commerce Website (Django + HTML/Bootstrap)

A fully functional **online shopping platform** built with **Django (Python)** as the backend and pure **HTML, SCSS, Bootstrap 5** as the frontend.

## Features

### User Features
- User registration & login (with OTP verification)
- Password reset & forgot password flow
- Browse products (Men, Women, Casual categories)
- Product details with variants & reviews
- Add to cart & wishlist
- Address management
- Checkout & multiple payment options (including Razorpay)
- Wallet system
- Order history & tracking

### Admin Dashboard
- Complete product, variant, category & sub-category management
- Banner, coupon & offer management
- User management (block/unblock)
- Order management
- Sales reports with interactive charts (ApexCharts)
- Top-selling products & categories analytics

## Tech Stack

| Layer        | Technology                                      |
|--------------|--------------------------------------------------|
| Backend      | Django (Python)                                  |
| Frontend     | HTML5, SCSS, Bootstrap 5, jQuery                |
| Charts       | ApexCharts                                       |
| Styling      | Bootstrap, SimpleBar, Owl Carousel, AOS          |
| Icons        | IonIcons, Flaticon, Icomoon                      |
| Payments     | Razorpay integration                             |
| Database     | PostgreSQL |

## Project Structure (Key Folders)
├── node_modules/          # ApexCharts, Bootstrap, jQuery, SimpleBar
├── template/              # All HTML templates
│   ├── admin/             # Admin panel templates
│   └── user/              # User-facing pages
├── assets/                # Custom CSS, JS, images
├── static/
│   ├── css/               # Compiled & vendor CSS
│   ├── js/                # Custom + vendor JS
│   └── img/               # Product & site images
├── user/                  # User authentication app
├── user_app/              # Core e-commerce logic
├── wishlist/              # Wishlist functionality
└── manage.py


## Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/your-ecommerce-project.git
cd your-ecommerce-project

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install django pillow      # Add more if you have requirements.txt

# 4. Run migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create superuser (for admin access)
python manage.py createsuperuser

# 6. Run server
python manage.py runserver
