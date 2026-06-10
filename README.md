BuyNext 🛒

BuyNext is a full-featured multi-vendor e-commerce platform built with Django 5, enabling customers to shop online, sellers to manage their stores, and administrators to oversee the entire marketplace from a centralized dashboard.

🚀 Features
👤 Customer Features
User Registration & Authentication
Google OAuth Login
Profile Management
Address Management
Product Search & Browsing
Shopping Cart
Wishlist & Collections
Secure Checkout
Razorpay Payment Integration
Order Placement & Tracking
Order History
Product Reviews & Ratings
🏪 Seller Features
Seller Registration & Verification
Seller Dashboard
Product Management
Product Variant Management
Inventory Management
Order Management
Earnings Dashboard
Offer & Discount Management
Customer Review Replies
Seller Profile & Settings
🛡️ Admin Features
Admin Dashboard
Customer Management
Seller Verification & Management
Product Verification & Approval
Order Monitoring
Category & Subcategory Management
Product Catalogue Management
Seller Performance Reports
Advanced Search & Analytics
🛠️ Tech Stack
Backend
Python
Django 5
Django Allauth
MySQL
Cloud & Storage
AWS S3 (Media Storage)
Payments
Razorpay
Authentication
Django Authentication
Google OAuth
Communication
Twilio SMS Integration
SMTP Email Service
📂 Project Structure
BuyNext/
│
├── BuyNext/          # Project Settings
├── customer/         # Customer Module
├── seller/           # Seller Module
├── bnadmin/          # Admin Module
├── core/             # Core Application
├── templates/        # HTML Templates
├── manage.py
└── requirements.txt
⚙️ Installation
1️⃣ Clone the Repository
git clone https://github.com/your-username/BuyNext.git
cd BuyNext
2️⃣ Create Virtual Environment
python -m venv venv
3️⃣ Activate Virtual Environment
Windows
venv\Scripts\activate
Linux/Mac
source venv/bin/activate
4️⃣ Install Dependencies
pip install -r requirements.txt
5️⃣ Configure Environment Variables

Create a .env file in the root directory:

SECRET_KEY=your_secret_key

DEBUG=True

EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_password

TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=your_number

RAZORPAY_KEY_ID=your_key
RAZORPAY_KEY_SECRET=your_secret

AWS_STORAGE_BUCKET_NAME=your_bucket
AWS_S3_REGION_NAME=your_region

GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
6️⃣ Configure Database

Update settings.py with your MySQL credentials.

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
7️⃣ Run Migrations
python manage.py makemigrations
python manage.py migrate
8️⃣ Create Superuser
python manage.py createsuperuser
9️⃣ Run Server
python manage.py runserver

Visit:

http://127.0.0.1:8000
* Environment Variables
Variable	Description
SECRET_KEY	Django Secret Key
DEBUG	Debug Mode
EMAIL_HOST_USER	SMTP Email
EMAIL_HOST_PASSWORD	SMTP Password
TWILIO_ACCOUNT_SID	Twilio SID
TWILIO_AUTH_TOKEN	Twilio Token
TWILIO_PHONE_NUMBER	Twilio Phone Number
RAZORPAY_KEY_ID	Razorpay Key
RAZORPAY_KEY_SECRET	Razorpay Secret
AWS_STORAGE_BUCKET_NAME	S3 Bucket Name
AWS_S3_REGION_NAME	AWS Region
* Core Modules
Customer Module
Account Management
Cart
Wishlist
Checkout
Orders
Reviews
Seller Module
Product Management
Inventory Tracking
Order Fulfillment
Earnings & Analytics
Admin Module
User Management
Seller Verification
Product Approval
Marketplace Monitoring
* Future Enhancements
AI Product Recommendations
Advanced Analytics Dashboard
Coupon Management
Multi-Language Support
Real-Time Notifications
Mobile Application
 Author

Hamad N M

B.Tech Computer Science & Engineering

 Email: hamadnm111@gmail.com

💼 LinkedIn: Hamad N M LinkedIn

🐙 GitHub: https://github.com/HAMADNM/

📜 License

This project is developed for educational and portfolio purposes. Feel free to use and modify it according to your requirements.

⭐ If you found this project useful, consider giving it a star on GitHub!
