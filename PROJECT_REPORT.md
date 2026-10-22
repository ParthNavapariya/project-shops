# Comprehensive Project Documentation & Academic Report

## Project Title
**AI-Powered Pre-Owned Fashion Marketplace & Rental System (ReWear AI)**

---

## 1. Executive Summary & Abstract
The fashion and textile industry is the second-largest polluter globally, generating over 92 million tons of textile waste annually and contributing to 10% of global carbon emissions. Despite the growth of the secondhand clothing market, consumers and sellers face two primary obstacles: **pricing ambiguity** (uncertainty regarding fair valuation of used luxury and everyday garments) and **limited flexibility** (the inability to rent occasion wear without committing to permanent purchases).

**ReWear AI** resolves these challenges by combining:
1. An intelligent **Machine Learning Valuation Engine** (`Scikit-Learn` Gradient Boosting) that predicts fair resale prices and optimal daily rental rates based on multi-parameter attributes (brand tier prestige, garment age decay, condition grading, material durability, and market demand).
2. A dual-mode circular marketplace supporting both **resale purchases** and **short-term event rentals** with automated refundable security deposit logistics.
3. An environmental impact tracking system calculating precise **CO₂ emissions diverted** and **clean water saved** for every circular transaction.

---

## 2. Project Objectives
- **Algorithmic Pricing Transparency**: Eliminate arbitrary pricing by sellers through automated machine learning price discovery.
- **Buyer Decision Support**: Provide dynamic **"Deal Quality Badges"** (*Great Deal*, *Fair Value*, *Above Market*) and 4-year depreciation curves.
- **Circular Fashion & Clothing Reuse**: Divert garments from landfills by facilitating short-term rentals for single-use occasion garments (gowns, tuxedos, outerwear).
- **End-to-End Order & Return Logistics**: Provide transparent tracking timelines and one-click prepaid return label generation.
- **Measurable Sustainability**: Gamify circular fashion adoption through user Eco-Points and planetary carbon/water metrics.

---

## 3. Technology Stack & Specifications

| Dimension | Specification | Rationale |
|---|---|---|
| **Backend Framework** | Python 3.14 + Flask 3.1 | Lightweight, extensible WSGI framework with clean RESTful API routing |
| **Database** | MySQL / SQLite + Flask-SQLAlchemy 3.1 | Relational database modeling with automated cross-platform fallback |
| **Machine Learning** | Scikit-learn, Pandas, NumPy, Joblib | Gradient Boosting Regressor with OneHotEncoding and StandardScaler pipelines |
| **Frontend Technologies** | HTML5, CSS3, Vanilla JavaScript, Bootstrap 5.3 | Responsive modern design system with glassmorphism and micro-animations |
| **Data Visualization** | Chart.js | Real-time interactive charts (48-month depreciation, seller earnings, category split) |
| **Security & Auth** | Werkzeug Security | Scrypt/PBKDF2 salted password hashing with session-based access control |

---

## 4. Machine Learning Model Architecture

### 4.1 Feature Engineering

```
Input Vector X:
├── Categorical Features:
│   ├── brand (e.g. Burberry, Gucci, Saint Laurent, Nike, Zara, Patagonia)
│   ├── brand_tier (Luxury, Premium, Sustainable, Sportswear, Heritage, FastFashion)
│   ├── category (Jackets & Coats, Dresses & Gowns, Suits, Shoes, Bags, Denim)
│   ├── condition (Brand New with Tags, Like New, Gently Used, Fair / Well Used)
│   ├── usage_frequency (Rarely, Occasionally, Frequently)
│   └── material (Leather, Cashmere, Silk, Wool, Cotton, Denim, Polyester)
└── Numerical Features:
    ├── original_price (Retail MSRP in USD/INR)
    └── age_months (Garment age in months, 1 to 48+)
```

### 4.2 Algorithm & Preprocessing Pipeline
- **Categorical Processing**: `OneHotEncoder(handle_unknown='ignore', sparse_output=False)`
- **Numerical Scaling**: `StandardScaler()`
- **Estimator**: `GradientBoostingRegressor(n_estimators=180, learning_rate=0.08, max_depth=5, random_state=42)`
- **Validation Metrics**:
  - **R² Score**: `0.9825` (High explanatory variance)
  - **Mean Absolute Error (MAE)**: `~$18.08`

### 4.3 Derivative Business Metrics
1. **Fair Resale Price**: $\hat{y} = \text{Model}(X)$
2. **Confidence Range**: $[\hat{y} \times 0.88, \; \hat{y} \times 1.12]$
3. **Daily Rental Rate**: $R_{\text{daily}} = \max(8.0, \; \hat{y} \times 0.038)$
4. **Refundable Security Deposit**: $D = \max(20.0, \; \hat{y} \times 0.45)$
5. **Depreciation Curve Generation**: Evaluates $\hat{y}$ at $t \in [0, 3, 6, 12, 18, 24, 36, 48]$ months to render continuous residual graphs.

---

## 5. System Architecture & Data Flow

```mermaid
flowchart TD
    User([User / Browser])
    
    subgraph Frontend [Presentation Layer]
        UI[Bootstrap 5 + CSS Tokens]
        Charts[Chart.js Visualizations]
        Pickers[Rental Date & Price JS]
    end

    subgraph Backend [Flask Application Server]
        Auth[Session Auth & RBAC]
        MarketRoutes[Marketplace & Search Controller]
        RentalEngine[Booking & Date Math Controller]
        OrdersEngine[Order Tracker & Return Manager]
        AIApi[/api/ai/estimate-price]
    end

    subgraph ML_Layer [Scikit-learn Engine]
        Model[(Gradient Boosting Pipeline)]
        Deprecator[Depreciation Timeline Generator]
        DealEvaluator[Deal Quality Analyzer]
    end

    subgraph Database [Storage Layer]
        DB[(MySQL / SQLite)]
        Tables[Users, Products, Orders, Rentals, Reviews, Wishlists]
    end

    User --> UI
    UI --> MarketRoutes
    UI --> AIApi
    AIApi --> Model
    Model --> Deprecator
    Deprecator --> Charts
    MarketRoutes --> DB
    RentalEngine --> DB
    OrdersEngine --> DB
```

---

## 6. Database Entity-Relationship (ER) Design

1. **`users`**: User ID, Name, Email, Hashed Password, Role (Buyer, Seller, Both), Bio, Phone, City, Eco-Points.
2. **`categories`**: Category ID, Name, URL Slug, Icon, Description.
3. **`products`**: Product ID, Title, Brand, Category ID (FK), Size, Color, Material, Original MSRP, Listed Asking Price, AI Estimated Fair Value, AI Min/Max Range, Rental Daily Rate, Rental Security Deposit, Age Months, Condition, Usage Frequency, Flaws Disclosure, Primary Image, CO2 Saved, Water Saved, Seller ID (FK), Status Flags (`is_sold`, `is_currently_rented`).
4. **`orders`**: Order ID, Unique Tracking Number, Buyer ID (FK), Product ID (FK), Order Type (`Buy` / `Rent`), Total Amount, Payment Method, Delivery Address, Order Status Lifecycle (`Placed` → `Processing` → `Shipped` → `Delivered` → `Rental Active` → `Return Initiated` → `Completed`).
5. **`rental_bookings`**: Booking ID, Order ID (FK), Product ID (FK), Renter ID (FK), Start Date, Return Date, Total Days, Daily Rate, Security Deposit, Rental Status, Deposit Refund Flag.
6. **`return_requests`**: Return ID, Order ID (FK), User ID (FK), Return Type, Reason, Prepaid Courier Return Tracking ID, Status.
7. **`reviews`**: Review ID, Product ID (FK), User ID (FK), Rating (1-5 stars), Title, Comment, Verified Badge.
8. **`wishlists`**: Unique pair of User ID and Product ID.

---

## 7. Key Modules & Functional Description

### 7.1 Home & AI Quick Predictor (`/`)
- Dynamic hero banner with real-time community sustainability metrics.
- Embedded interactive **Quick AI Predictor** allowing visitors to test price estimates without navigating away.
- **AI Spotlight**: Surfaces top-rated deals with automatic percentage-off-retail tags.

### 7.2 Catalog & Multi-Criteria Filtering (`/marketplace`)
- Dual-mode tabs: **All Items**, **Buy Pre-Owned**, and **Rent Only**.
- Multi-dimensional filters: Category, Brand, Garment Condition, Size, and AI Deal Rating (*Great Deal*, *Fair Price*).

### 7.3 Product Detail & AI Valuation Studio (`/product/<id>`)
- High-resolution imagery, garment specifications, and seller disclosures.
- **AI Valuation Studio**: Displays AI fair benchmark, confidence intervals, and expandable 4-year depreciation curve.
- Dual-action tabs for instant checkout or custom rental date selection with live deposit breakdown.

### 7.4 Product Comparison Matrix (`/compare`)
- Side-by-side comparison of up to 4 fashion items across 8 dimensions (Asking Price, AI Valuation, Deal Quality, Daily Rental, Condition, Material, CO₂ & Water Savings).

### 7.5 Standalone AI Valuation Lab (`/ai-lab`)
- Interactive studio with sliders for Original Retail MSRP ($50 - $4,000) and Garment Age (1 - 48 months).
- Real-time `Chart.js` residual curves and Rental Breakeven ROI calculation (days to recover 100% of purchase price).

### 7.6 Order Tracking & Return Management (`/orders`, `/order/<id>`)
- Visual multi-stage order tracking progress bar.
- One-click prepaid return label generation with automated courier pickup scheduling.

### 7.7 Seller Wardrobe Studio (`/seller/dashboard`)
- Revenue tracking, active rental monitoring, and performance analytics (Listing Views vs Gross Earnings, Category Split Donut Chart).

### 7.8 Planetary Sustainability Dashboard (`/eco-impact`)
- Cumulative metrics: CO₂ emissions prevented, water conserved, and items diverted from landfills.
- Personal user footprint tracking with gamified Eco-Point tiers.

---

## 8. Viva & Project Defense Guide (Sample Q&A)

**Q1: Why did you choose Gradient Boosting over standard Linear Regression?**  
*Answer*: Fashion garment depreciation is non-linear. Fast-fashion brands depreciate exponentially within the first 6 months, whereas archival luxury brands (like Gucci or Burberry) retain value or plateau due to brand prestige. Gradient Boosting decision trees effectively capture these non-linear feature interactions (Brand Tier × Material × Age Decay) without requiring complex manual polynomial transformations.

**Q2: How does the system ensure rental deposits are protected?**  
*Answer*: The platform models a two-part payment: the rental usage fee and a refundable security deposit. When an item is returned and inspected, the system updates the booking status to `Inspected & Returned` and releases the deposit back to the customer's payment method.

**Q3: How are sustainability metrics calculated?**  
*Answer*: Each apparel category has established textile manufacturing benchmarks (e.g., producing a new pair of jeans requires ~7,600 liters of water and emits ~11 kg of CO₂; a wool blazer emits ~24 kg of CO₂). By reusing an existing piece, ReWear credits the saved manufacturing footprint to both the transaction and the user's profile.

**Q4: How does the system handle database portability?**  
*Answer*: Through [config.py](file:///Users/parthnavapariya/Documents/project-nandni/config.py) and [models.py](file:///Users/parthnavapariya/Documents/project-nandni/models.py), the platform supports full production **MySQL** connections via `PyMySQL`, while providing an automatic fallback to local **SQLite** (`preowned_fashion.db`). This ensures the project runs seamlessly on any evaluation machine without database setup friction.
