from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='both')  # buyer, seller, both, admin
    bio = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    profile_pic = db.Column(db.String(255), default='default_avatar.jpg')
    eco_points = db.Column(db.Integer, default=50)  # Gamified sustainable fashion points
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    products = db.relationship('Product', backref='seller', lazy=True, foreign_keys='Product.seller_id')
    orders = db.relationship('Order', backref='buyer', lazy=True, foreign_keys='Order.buyer_id')
    reviews = db.relationship('Review', backref='author', lazy=True)
    wishlist_items = db.relationship('Wishlist', backref='user', lazy=True, cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.name} ({self.email})>'


class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    slug = db.Column(db.String(80), nullable=False, unique=True)
    icon = db.Column(db.String(50), default='bi-tag')
    description = db.Column(db.String(255), nullable=True)
    
    products = db.relationship('Product', backref='category_rel', lazy=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    brand = db.Column(db.String(100), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    gender = db.Column(db.String(20), default='Unisex')  # Women, Men, Unisex, Kids
    size = db.Column(db.String(20), nullable=False)      # XS, S, M, L, XL, XXL, Free Size
    color = db.Column(db.String(50), nullable=False)
    material = db.Column(db.String(80), default='Cotton')
    
    # Financial & AI Valuation attributes
    original_price = db.Column(db.Float, nullable=False)     # Retail MSRP ($)
    listed_price = db.Column(db.Float, nullable=False)       # Seller's asking price ($)
    estimated_fair_price = db.Column(db.Float, nullable=True) # AI predicted fair resale price ($)
    ai_min_price = db.Column(db.Float, nullable=True)        # AI lower price boundary
    ai_max_price = db.Column(db.Float, nullable=True)        # AI upper price boundary
    
    # Rental attributes
    is_available_for_resale = db.Column(db.Boolean, default=True)
    is_available_for_rent = db.Column(db.Boolean, default=True)
    rental_price_per_day = db.Column(db.Float, default=15.0)  # Daily rental fee ($)
    rental_security_deposit = db.Column(db.Float, default=50.0) # Refundable deposit ($)
    
    # Item lifecycle & condition
    age_months = db.Column(db.Integer, default=6)            # Age of garment in months
    condition = db.Column(db.String(50), nullable=False)     # 'New with tags', 'Like New', 'Gently Used', 'Well Used'
    usage_frequency = db.Column(db.String(50), default='Occasionally') # 'Rarely', 'Occasionally', 'Frequently'
    flaws_description = db.Column(db.String(255), default='None. Clean & sanitized.')
    
    # Inventory state
    is_sold = db.Column(db.Boolean, default=False)
    is_currently_rented = db.Column(db.Boolean, default=False)
    
    # Media
    primary_image = db.Column(db.String(255), nullable=False)
    additional_images = db.Column(db.Text, nullable=True)    # Comma-separated or JSON list
    
    # Eco metrics (derived based on garment type and reuse)
    co2_saved_kg = db.Column(db.Float, default=7.5)          # Est. CO2 saved in kg
    water_saved_liters = db.Column(db.Float, default=2700.0) # Est. water saved in liters
    
    # Metadata
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    views_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='product', lazy=True)
    reviews = db.relationship('Review', backref='product', lazy=True, cascade='all, delete-orphan')
    wishlist_entries = db.relationship('Wishlist', backref='product', lazy=True, cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def discount_pct(self):
        if self.original_price and self.original_price > 0:
            diff = self.original_price - self.listed_price
            return max(0, round((diff / self.original_price) * 100))
        return 0

    @property
    def deal_rating(self):
        """AI price evaluation deal rating"""
        fair = self.estimated_fair_price or self.listed_price
        if not fair or fair <= 0:
            return {"label": "Fair Value", "class": "badge-fair", "score": 75}
            
        ratio = self.listed_price / fair
        if ratio < 0.85:
            return {"label": "Great Deal", "class": "badge-great-deal", "score": 95, "desc": f"{(1 - ratio)*100:.0f}% below AI fair value"}
        elif ratio <= 1.12:
            return {"label": "Fair Price", "class": "badge-fair", "score": 82, "desc": "Priced accurately to current market"}
        else:
            return {"label": "Above Market", "class": "badge-above-market", "score": 55, "desc": f"{(ratio - 1)*100:.0f}% above AI fair value"}

    @property
    def average_rating(self):
        if not self.reviews:
            return 4.8  # Default positive community rating if new
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)

    @property
    def review_count(self):
        return len(self.reviews)

    def __repr__(self):
        return f'<Product {self.title} by {self.brand}>'


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    order_type = db.Column(db.String(20), default='Buy')  # 'Buy' or 'Rent'
    
    # Financials
    item_price = db.Column(db.Float, nullable=False)
    shipping_fee = db.Column(db.Float, default=4.99)
    security_deposit = db.Column(db.Float, default=0.0)   # For rentals
    total_amount = db.Column(db.Float, nullable=False)
    
    # Delivery & Contact
    shipping_address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), default='New York')
    postal_code = db.Column(db.String(20), default='10001')
    contact_phone = db.Column(db.String(25), nullable=False)
    
    # Payment & Status
    payment_status = db.Column(db.String(30), default='Paid')     # 'Paid', 'Pending', 'Refunded'
    payment_method = db.Column(db.String(50), default='Credit Card') # 'Credit Card', 'UPI', 'PayPal'
    
    # Order Status Lifecycle:
    # 'Placed' -> 'Processing' -> 'Shipped' -> 'Delivered' -> 'Rental Active' -> 'Return In Progress' -> 'Completed'
    order_status = db.Column(db.String(40), default='Placed')
    
    tracking_number = db.Column(db.String(50), nullable=True)
    courier_partner = db.Column(db.String(50), default='EcoExpress Logistics')
    estimated_delivery = db.Column(db.Date, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    rental_detail = db.relationship('RentalBooking', backref='order_rel', uselist=False, lazy=True)
    return_request = db.relationship('ReturnRequest', backref='order_rel', uselist=False, lazy=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f'<Order {self.order_number} ({self.order_type})>'


class RentalBooking(db.Model):
    __tablename__ = 'rental_bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    renter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_days = db.Column(db.Integer, nullable=False, default=3)
    daily_rate = db.Column(db.Float, nullable=False)
    security_deposit = db.Column(db.Float, nullable=False)
    total_rent = db.Column(db.Float, nullable=False)
    
    # Return lifecycle: 'Active', 'Due Soon', 'Return Requested', 'Returned & Inspected', 'Overdue'
    rental_status = db.Column(db.String(40), default='Active')
    deposit_refunded = db.Column(db.Boolean, default=False)
    return_tracking_number = db.Column(db.String(50), nullable=True)
    return_notes = db.Column(db.Text, nullable=True)
    returned_at = db.Column(db.DateTime, nullable=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f'<RentalBooking Order#{self.order_id} ({self.total_days} days)>'


class ReturnRequest(db.Model):
    __tablename__ = 'return_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    return_type = db.Column(db.String(30), default='Rental Return') # 'Rental Return' or 'Resale Return'
    reason = db.Column(db.String(100), nullable=False) # 'End of Rental', 'Size Did Not Fit', 'Condition Mismatch', 'Defective'
    notes = db.Column(db.Text, nullable=True)
    
    # Status: 'Requested', 'Approved - Label Generated', 'Picked Up', 'Delivered to Hub', 'Inspected - Refunded'
    status = db.Column(db.String(40), default='Requested')
    return_tracking_id = db.Column(db.String(60), nullable=True)
    refund_amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f'<ReturnRequest Order#{self.order_id} [{self.status}]>'


class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False) # 1 to 5
    title = db.Column(db.String(120), nullable=True)
    comment = db.Column(db.Text, nullable=False)
    is_verified_experience = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f'<Review {self.rating}* by User#{self.user_id}>'


class Wishlist(db.Model):
    __tablename__ = 'wishlists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='uq_user_product_wishlist'),)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f'<Wishlist User#{self.user_id} Product#{self.product_id}>'
