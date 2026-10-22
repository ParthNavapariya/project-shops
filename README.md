# ReWear AI: Pre-Owned Fashion Marketplace & Rental System

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask%203.1-black.svg)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/AI%2FML-Scikit--learn%201.9-orange.svg)](https://scikit-learn.org/)
[![Database](https://img.shields.io/badge/Database-MySQL%20%7C%20SQLite-blue.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

An innovative AI-powered circular fashion platform designed to make buying, selling, and renting pre-owned clothing convenient, affordable, and environmentally sustainable. The platform employs machine learning regression models to evaluate the fair resale and rental value of garments based on brand tier, category, original price, age decay, condition grade, and wear frequency.

---

## 🌟 Key Features

### 1. 🤖 AI-Powered Fair Resale & Rental Valuation Engine
- **Machine Learning Architecture**: Built using `Scikit-learn` (Gradient Boosting Regressor) and `Pandas`/`NumPy` with full data pipelines (One-Hot Encoding, Standard Scaling, and Residual Analysis).
- **Valuation Metrics**: Predicts fair resale price ($), minimum/maximum market confidence range, suggested daily rental rates, and refundable security deposit.
- **Deal Rating Badges**: Evaluates whether any listed asking price represents a **"Great Deal"** (>15% below market), **"Fair Price"**, or **"Above Market"**.
- **Interactive 48-Month Depreciation Curves**: Visualizes garment value retention over 4 years using `Chart.js`.

### 2. 👗 Integrated Buy & Rent Marketplace
- **Dual Mode Filter**: Toggle seamlessly between **Buy Pre-Owned** and **Rent Designer Wear**.
- **Faceted Filters**: Filter by Category (Dresses, Jackets, Suits, Shoes, Bags, Denim, Knits, Ethnic wear), Brand (Luxury, Heritage, Sportswear, Sustainable), Condition, Size, and AI Deal ratings.
- **Side-by-Side Comparison Matrix (`/compare`)**: Compare up to 4 garments side-by-side on specs, AI valuations, rental terms, and carbon footprint.

### 3. 📅 Rental Booking & Date Management
- **Interactive Calendar Duration Picker**: Auto-calculates rental duration, daily rates, and refundable security deposits.
- **Damage Protection & Cleaning**: All rentals include professional sanitization and insured shipping.

### 4. 📦 Order Tracking & Return Management
- **Visual Progress Timeline**: Real-time status tracking from *Confirmed* → *Inspected* → *Dispatched* → *Delivered* → *Rental Active* → *Return Initiated*.
- **One-Click Return Label Generator**: Generates prepaid carbon-neutral courier return labels for rental returns or purchase disputes.

### 5. 📊 Seller Studio & Analytics Dashboard (`/seller/dashboard`)
- **Wardrobe Monetization**: Track total earnings, active rentals, and completed orders.
- **Data Visualizations**: `Chart.js` line charts for listing views vs earnings and donut charts for wardrobe category distribution.
- **AI Listing Wizard (`/sell`)**: Live "Compute Fair Value" button auto-populates optimal selling and rental rates.

### 6. 🌱 Circular Fashion Eco-Impact Tracker (`/eco-impact`)
- Calculates exact environmental savings per garment: **CO₂ prevented (kg)** and **clean water saved (liters)** vs manufacturing new clothing.
- Community Eco-Point gamification system rewarding users for circular reuse.

---

## 🛠️ Technology Stack

| Category | Technology |
|---|---|
| **Programming Languages** | Python 3.14, JavaScript (ES6+) |
| **Web Framework** | Flask, Flask-SQLAlchemy, Werkzeug |
| **Frontend Styling** | HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons |
| **AI / Machine Learning** | Scikit-learn, Pandas, NumPy, Joblib |
| **Data Visualization** | Chart.js, Matplotlib |
| **Database** | MySQL (with seamless SQLite zero-config fallback) |
| **Authentication** | Secure password hashing (`Werkzeug.security`) with session management |

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- (Optional) MySQL Server (if using MySQL instead of local SQLite)

### 2. Installation
```bash
# Navigate to project directory
cd project-nandni

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Configuration
By default, the platform runs instantly out-of-the-box on a local SQLite database (`preowned_fashion.db`).

If you wish to connect to your local **MySQL** database:
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Set your MySQL credentials in `.env`:
   ```env
   USE_MYSQL=true
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DB=preowned_fashion_db
   ```
3. Initialize the database and load realistic seed data:
   ```bash
   python3 init_db.py
   ```

### 4. Retraining the Machine Learning Model (Optional)
```bash
python3 -c "from ml_engine import price_model; price_model.train()"
```

### 5. Running the Application
```bash
python3 app.py
```
Open your browser and navigate to:
**`http://127.0.0.1:5001`**

---

## 👥 Demo User Accounts (One-Click Sign In Available)

On the `/login` page, you can use the **⚡ One-Click Instant Sign-In** buttons or credentials:

| Name | Role | Email | Password |
|---|---|---|---|
| **Sophia Laurent** | Stylist & Seller | `sophia@example.com` | `password123` |
| **Marcus Vance** | Collector / Curator | `marcus@example.com` | `password123` |
| **Elena Rostova** | Occasion Renter | `elena@example.com` | `password123` |
| **Nandni Patel** | AI Researcher | `nandni@example.com` | `password123` |

---

## 📂 Project Architecture

```
project-nandni/
├── app.py                     # Main Flask web application & API routing
├── config.py                  # Database & environment configurations
├── models.py                  # SQLAlchemy schema (User, Product, Order, Rental, Review, Wishlist)
├── ml_engine.py               # Scikit-learn Gradient Boosting pricing model & residual timeline
├── seed_data.py               # Pre-populated curated luxury pieces, rentals, users & reviews
├── init_db.py                 # Database initialization and schema builder
├── requirements.txt           # Python dependencies
├── ml_models/
│   └── fair_resale_model.joblib # Serialized ML pipeline model
├── static/
│   ├── css/
│   │   └── style.css          # Modern luxury design system, tokens, and animations
│   └── js/
│       ├── main.js            # Wishlist toggles, comparison dock & toast notifications
│       ├── ai_estimator.js    # Live AI valuation requester & Chart.js graph renderer
│       └── rental_picker.js   # Dynamic rental calendar & deposit math
└── templates/
    ├── base.html              # Core navigation layout, category bar, footer
    ├── index.html             # Landing page with interactive hero AI estimator
    ├── marketplace.html       # Dual-mode catalog with faceted filters
    ├── product_detail.html    # Garment detail, AI valuation card & rental booking
    ├── compare.html           # Side-by-side comparison matrix
    ├── ai_lab.html            # Standalone ML Valuation Studio with dynamic sliders
    ├── sell.html              # AI-assisted listing wizard
    ├── wishlist.html          # User wishlist
    ├── checkout.html          # Purchase & rental booking checkout
    ├── orders.html            # Orders & active rentals list
    ├── order_detail.html      # Visual timeline tracker & return request modal
    ├── seller_dashboard.html  # Seller analytics & Chart.js earnings charts
    ├── eco_impact.html        # Sustainability carbon & water savings dashboard
    ├── login.html             # Sign in with instant 1-click demo logins
    └── register.html          # User registration
```
