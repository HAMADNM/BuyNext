# BuyNext 🛒

## Multi-Vendor E-Commerce Marketplace

BuyNext is a feature-rich multi-vendor e-commerce platform built using Django 5, designed to provide a seamless online shopping experience for customers while empowering sellers and administrators with powerful management tools.

The platform supports customer shopping, seller storefront management, secure payments, order processing, and marketplace administration within a single ecosystem.

🌐 **Live Demo:** https://buynext.hamadnm.online/

---

## 🚀 Features

### 👤 Customer Features

* User Registration & Authentication
* Google OAuth Login
* Profile Management
* Address Management
* Product Search & Filtering
* Shopping Cart
* Wishlist Management
* Secure Checkout
* Razorpay Payment Integration
* Order Placement & Tracking
* Order History
* Product Reviews & Ratings

### 🏪 Seller Features

* Seller Registration & Verification
* Seller Dashboard
* Product Management
* Product Variant Management
* Inventory Management
* Order Processing
* Earnings Dashboard
* Offer & Discount Management
* Customer Review Replies
* Seller Profile Management

### 🛡️ Admin Features

* Admin Dashboard
* Customer Management
* Seller Verification & Management
* Product Approval System
* Order Monitoring
* Category & Subcategory Management
* Product Catalog Management
* Seller Performance Analytics
* Marketplace Administration

---

## 🛠️ Tech Stack

### Backend

* Python
* Django 5
* Django Allauth
* MySQL

### Authentication

* Django Authentication
* Google OAuth

### Payments

* Razorpay Payment Gateway

### Cloud Storage

* AWS S3

### Communication Services

* Twilio SMS Integration
* SMTP Email Service

---

## 📂 Project Structure

```bash
BuyNext/
│
├── BuyNext/          # Project Configuration
├── customer/         # Customer Module
├── seller/           # Seller Module
├── bnadmin/          # Admin Module
├── core/             # Core Functionality
├── templates/        # HTML Templates
├── static/           # Static Files
├── media/            # Media Files
├── manage.py
└── requirements.txt
```

---

## ⚙️ Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/HAMADNM/BuyNext.git
cd BuyNext
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your_secret_key

DEBUG=True

EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_password

TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=your_phone_number

RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret

AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION_NAME=your_region

GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
```

### 6. Configure Database

Update your database settings in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'buynext',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 7. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. Create Superuser

```bash
python manage.py createsuperuser
```

### 9. Run Development Server

```bash
python manage.py runserver
```

Open your browser and visit:

```text
http://127.0.0.1:8000/
```

---

## 🔐 Environment Variables

| Variable                | Description                 |
| ----------------------- | --------------------------- |
| SECRET_KEY              | Django Secret Key           |
| DEBUG                   | Debug Mode                  |
| EMAIL_HOST_USER         | SMTP Email                  |
| EMAIL_HOST_PASSWORD     | SMTP Password               |
| TWILIO_ACCOUNT_SID      | Twilio Account SID          |
| TWILIO_AUTH_TOKEN       | Twilio Authentication Token |
| TWILIO_PHONE_NUMBER     | Twilio Phone Number         |
| RAZORPAY_KEY_ID         | Razorpay Key ID             |
| RAZORPAY_KEY_SECRET     | Razorpay Secret Key         |
| AWS_STORAGE_BUCKET_NAME | AWS S3 Bucket Name          |
| AWS_S3_REGION_NAME      | AWS Region                  |

---

## 📦 Core Modules

### Customer Module

* Account Management
* Shopping Cart
* Wishlist
* Checkout
* Order Management
* Reviews & Ratings

### Seller Module

* Product Management
* Inventory Tracking
* Order Fulfillment
* Earnings Analytics

### Admin Module

* User Management
* Seller Verification
* Product Approval
* Marketplace Monitoring

---

## 🔮 Future Enhancements

* AI-Based Product Recommendations
* Advanced Business Analytics
* Coupon & Promotional System
* Multi-Language Support
* Real-Time Notifications
* Mobile Application

---

## 👨‍💻 Author

**Hamad N M**

B.Tech Computer Science & Engineering

📧 Email: [hamadnm111@gmail.com](mailto:hamadnm111@gmail.com)

💼 LinkedIn: https://www.linkedin.com/in/hamadnm

🐙 GitHub: https://github.com/HAMADNM

---

## 📜 License

This project is developed for educational and portfolio purposes. Feel free to use, modify, and enhance it according to your requirements.

---

⭐ If you found this project useful, please consider giving it a star on GitHub.
