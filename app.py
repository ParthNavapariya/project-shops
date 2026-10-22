import os
import sys
import glob
import site

# Automatically load local venv site-packages if running with system python
_VENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv')
if os.path.exists(_VENV_PATH):
    for _sp in glob.glob(os.path.join(_VENV_PATH, 'lib', 'python*', 'site-packages')):
        if _sp not in sys.path:
            site.addsitedir(_sp)

import uuid
from datetime import datetime, timedelta
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, jsonify, session, g
)
from werkzeug.utils import secure_filename
from config import Config
from models import (
    db, User, Category, Product, Order,
    RentalBooking, ReturnRequest, Review, Wishlist
)
from ml_engine import price_model

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Safe database initialization with automatic SQLite fallback
if app.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('mysql'):
    try:
        from sqlalchemy import create_engine
        _engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], connect_args={'connect_timeout': 2})
        with _engine.connect():
            pass
    except Exception as _e:
        print(f"Notice: MySQL connection not active ({_e}). Using local SQLite database (preowned_fashion.db).")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///preowned_fashion.db'

try:
    db.init_app(app)
except Exception as e:
    print(f"Notice during db.init_app: {e}")

# Helper to check allowed image files
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Load logged-in user in session
@app.before_request
def load_current_user():
    user_id = session.get('user_id')
    if user_id:
        g.user = db.session.get(User, user_id)
    else:
        g.user = None
        
    # Initialize comparison list in session if missing
    if 'compare_ids' not in session:
        session['compare_ids'] = []

# Context processor for global template variables (wishlist count, compare count, categories)
@app.context_processor
def inject_global_data():
    wishlist_count = 0
    if g.user:
        wishlist_count = Wishlist.query.filter_by(user_id=g.user.id).count()
        
    compare_count = len(session.get('compare_ids', []))
    all_categories = Category.query.order_by(Category.name).all()
    
    return {
        'current_user': g.user,
        'wishlist_count': wishlist_count,
        'compare_count': compare_count,
        'nav_categories': all_categories,
        'now': datetime.utcnow()
    }


# =========================================================================
# 1. HOME & LANDING
# =========================================================================
@app.route('/')
def index():
    # Featured great deals
    featured_products = Product.query.filter_by(is_sold=False).order_by(Product.views_count.desc()).limit(8).all()
    
    # Rental spotlight
    rental_highlights = Product.query.filter_by(is_sold=False, is_available_for_rent=True).limit(4).all()
    
    # Calculate marketplace impact stats
    total_co2 = sum(p.co2_saved_kg for p in featured_products) + 420.5
    total_water = sum(p.water_saved_liters for p in featured_products) + 125000
    total_reused = Product.query.count() + 184
    
    return render_template(
        'index.html',
        featured_products=featured_products,
        rental_highlights=rental_highlights,
        total_co2=round(total_co2, 1),
        total_water=round(total_water),
        total_reused=total_reused
    )


# =========================================================================
# 2. MARKETPLACE BROWSING & SEARCH
# =========================================================================
@app.route('/marketplace')
def marketplace():
    category_slug = request.args.get('category', '').strip()
    brand_filter = request.args.get('brand', '').strip()
    condition_filter = request.args.get('condition', '').strip()
    size_filter = request.args.get('size', '').strip()
    mode = request.args.get('mode', 'all').strip()  # 'all', 'buy', 'rent'
    deal_filter = request.args.get('deal', '').strip()  # 'great', 'fair'
    search_query = request.args.get('q', '').strip()
    sort_by = request.args.get('sort', 'newest').strip()
    
    query = Product.query.filter_by(is_sold=False)
    
    # Mode filter
    if mode == 'buy':
        query = query.filter_by(is_available_for_resale=True)
    elif mode == 'rent':
        query = query.filter_by(is_available_for_rent=True, is_currently_rented=False)
        
    # Category filter
    selected_category = None
    if category_slug:
        selected_category = Category.query.filter_by(slug=category_slug).first()
        if selected_category:
            query = query.filter_by(category_id=selected_category.id)
            
    # Brand filter
    if brand_filter:
        query = query.filter(Product.brand.ilike(f"%{brand_filter}%"))
        
    # Condition filter
    if condition_filter:
        query = query.filter(Product.condition == condition_filter)
        
    # Size filter
    if size_filter:
        query = query.filter(Product.size == size_filter)
        
    # Search query
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Product.title.ilike(search_pattern),
                Product.brand.ilike(search_pattern),
                Product.description.ilike(search_pattern),
                Product.color.ilike(search_pattern)
            )
        )
        
    # Sorting
    if sort_by == 'price_low':
        query = query.order_by(Product.listed_price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Product.listed_price.desc())
    elif sort_by == 'discount':
        query = query.order_by((Product.original_price - Product.listed_price).desc())
    else: # newest
        query = query.order_by(Product.created_at.desc())
        
    products = query.all()
    
    # In-memory filter for AI deal rating if specified
    if deal_filter == 'great':
        products = [p for p in products if p.deal_rating['label'] == 'Great Deal']
    elif deal_filter == 'fair':
        products = [p for p in products if p.deal_rating['label'] in ('Great Deal', 'Fair Price')]

    # Unique available brands & sizes for filter dropdowns
    available_brands = sorted(list(set(p.brand for p in Product.query.with_entities(Product.brand).all())))
    
    return render_template(
        'marketplace.html',
        products=products,
        current_category=selected_category,
        available_brands=available_brands,
        selected_mode=mode,
        selected_brand=brand_filter,
        selected_condition=condition_filter,
        selected_size=size_filter,
        selected_sort=sort_by,
        selected_deal=deal_filter,
        search_query=search_query
    )


# =========================================================================
# 3. PRODUCT DETAIL & AI VALUATION BREAKDOWN
# =========================================================================
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for('marketplace'))
        
    # Increment view counter
    product.views_count = (product.views_count or 0) + 1
    db.session.commit()
    
    # Calculate detailed dynamic AI evaluation
    ai_valuation = price_model.predict_fair_price(
        brand=product.brand,
        category=product.category_rel.name if product.category_rel else 'General',
        original_price=product.original_price,
        age_months=product.age_months,
        condition=product.condition,
        usage_frequency=product.usage_frequency,
        material=product.material
    )
    
    # Deal quality evaluation
    deal_eval = price_model.evaluate_deal(product.listed_price, ai_valuation['fair_resale_price'])
    
    # Depreciation timeline for interactive chart
    depreciation_timeline = price_model.generate_depreciation_timeline(
        brand=product.brand,
        category=product.category_rel.name if product.category_rel else 'General',
        original_price=product.original_price,
        condition=product.condition,
        material=product.material
    )
    
    # User's wishlist status
    is_in_wishlist = False
    if g.user:
        is_in_wishlist = Wishlist.query.filter_by(user_id=g.user.id, product_id=product.id).first() is not None
        
    # Check if in comparison tray
    is_in_compare = product.id in session.get('compare_ids', [])
    
    # Similar products
    similar_products = Product.query.filter(
        Product.id != product.id,
        Product.category_id == product.category_id,
        Product.is_sold == False
    ).limit(4).all()
    
    return render_template(
        'product_detail.html',
        product=product,
        ai_valuation=ai_valuation,
        deal_eval=deal_eval,
        depreciation_timeline=depreciation_timeline,
        is_in_wishlist=is_in_wishlist,
        is_in_compare=is_in_compare,
        similar_products=similar_products
    )


# =========================================================================
# 4. AI ESTIMATION API & INTERACTIVE AI LAB
# =========================================================================
@app.route('/api/ai/estimate-price', methods=['POST'])
def api_estimate_price():
    data = request.get_json() or {}
    brand = data.get('brand', 'Other')
    category = data.get('category', 'Tops & Shirts')
    original_price = float(data.get('original_price', 100))
    age_months = int(data.get('age_months', 6))
    condition = data.get('condition', 'Gently Used')
    usage_frequency = data.get('usage_frequency', 'Occasionally')
    material = data.get('material', 'Cotton')
    
    result = price_model.predict_fair_price(
        brand=brand,
        category=category,
        original_price=original_price,
        age_months=age_months,
        condition=condition,
        usage_frequency=usage_frequency,
        material=material
    )
    
    timeline = price_model.generate_depreciation_timeline(
        brand=brand,
        category=category,
        original_price=original_price,
        condition=condition,
        material=material
    )
    
    result['timeline'] = timeline
    return jsonify({'success': True, 'data': result})


@app.route('/ai-lab')
def ai_lab():
    categories = Category.query.order_by(Category.name).all()
    brands = list(price_model.load() and [
        'Burberry', 'Saint Laurent', 'Gucci', 'Prada', 'Ralph Lauren',
        'Nike', 'Adidas', 'Jordan', 'Patagonia', 'Reformation',
        'Levi\'s', 'Zara', 'H&M', 'Mango', 'Other'
    ])
    return render_template('ai_lab.html', categories=categories, brands=brands)


# =========================================================================
# 5. PRODUCT COMPARISON SYSTEM
# =========================================================================
@app.route('/compare')
def compare():
    compare_ids = session.get('compare_ids', [])
    products = Product.query.filter(Product.id.in_(compare_ids)).all() if compare_ids else []
    
    # Build enriched comparison stats
    comparison_data = []
    for p in products:
        val = price_model.predict_fair_price(
            brand=p.brand,
            category=p.category_rel.name if p.category_rel else 'General',
            original_price=p.original_price,
            age_months=p.age_months,
            condition=p.condition,
            usage_frequency=p.usage_frequency,
            material=p.material
        )
        deal = price_model.evaluate_deal(p.listed_price, val['fair_resale_price'])
        comparison_data.append({
            'product': p,
            'valuation': val,
            'deal': deal
        })
        
    return render_template('compare.html', items=comparison_data)


@app.route('/api/compare/toggle', methods=['POST'])
def api_compare_toggle():
    data = request.get_json() or {}
    product_id = data.get('product_id')
    if not product_id:
        return jsonify({'success': False, 'message': 'Missing product id'}), 400
        
    compare_ids = session.get('compare_ids', [])
    
    if product_id in compare_ids:
        compare_ids.remove(product_id)
        action = 'removed'
    else:
        if len(compare_ids) >= 4:
            return jsonify({
                'success': False,
                'message': 'You can compare a maximum of 4 fashion products at once.'
            }), 400
        compare_ids.append(product_id)
        action = 'added'
        
    session['compare_ids'] = compare_ids
    session.modified = True
    
    return jsonify({
        'success': True,
        'action': action,
        'count': len(compare_ids)
    })


@app.route('/compare/clear')
def clear_compare():
    session['compare_ids'] = []
    session.modified = True
    flash("Comparison list cleared.", "info")
    return redirect(url_for('marketplace'))


# =========================================================================
# 6. SELL / LIST AN ITEM (WITH AI ASSISTANT)
# =========================================================================
@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if not g.user:
        flash("Please log in to list fashion items for sale or rent.", "warning")
        return redirect(url_for('login', next=url_for('sell')))
        
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        brand = request.form.get('brand', '').strip()
        category_id = int(request.form.get('category_id', 1))
        gender = request.form.get('gender', 'Unisex')
        size = request.form.get('size', 'M')
        color = request.form.get('color', '').strip()
        material = request.form.get('material', 'Cotton')
        original_price = float(request.form.get('original_price', 100))
        listed_price = float(request.form.get('listed_price', 50))
        age_months = int(request.form.get('age_months', 6))
        condition = request.form.get('condition', 'Gently Used')
        usage_frequency = request.form.get('usage_frequency', 'Occasionally')
        flaws_description = request.form.get('flaws_description', 'None. Immaculate condition.')
        description = request.form.get('description', '').strip()
        
        is_available_for_resale = bool(request.form.get('is_available_for_resale'))
        is_available_for_rent = bool(request.form.get('is_available_for_rent'))
        rental_price_per_day = float(request.form.get('rental_price_per_day', 15))
        rental_security_deposit = float(request.form.get('rental_security_deposit', 50))
        
        # Handle image upload or image URL
        primary_image = 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800&auto=format&fit=crop&q=80'
        image_url = request.form.get('image_url', '').strip()
        
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"{uuid.uuid4().hex[:10]}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                primary_image = url_for('static', filename=f"uploads/{filename}")
        elif image_url:
            primary_image = image_url

        # AI valuation calculation for records
        cat_obj = db.session.get(Category, category_id)
        cat_name = cat_obj.name if cat_obj else 'General'
        
        ai_val = price_model.predict_fair_price(
            brand=brand,
            category=cat_name,
            original_price=original_price,
            age_months=age_months,
            condition=condition,
            usage_frequency=usage_frequency,
            material=material
        )
        
        new_product = Product(
            title=title,
            description=description,
            brand=brand,
            category_id=category_id,
            gender=gender,
            size=size,
            color=color,
            material=material,
            original_price=original_price,
            listed_price=listed_price,
            estimated_fair_price=ai_val['fair_resale_price'],
            ai_min_price=ai_val['min_price'],
            ai_max_price=ai_val['max_price'],
            is_available_for_resale=is_available_for_resale,
            is_available_for_rent=is_available_for_rent,
            rental_price_per_day=rental_price_per_day,
            rental_security_deposit=rental_security_deposit,
            age_months=age_months,
            condition=condition,
            usage_frequency=usage_frequency,
            flaws_description=flaws_description,
            primary_image=primary_image,
            co2_saved_kg=ai_val['co2_saved_kg'],
            water_saved_liters=ai_val['water_saved_liters'],
            seller_id=g.user.id
        )
        
        # Award eco-points to the seller for listing pre-owned
        g.user.eco_points = (g.user.eco_points or 0) + 25
        
        db.session.add(new_product)
        db.session.commit()
        
        flash(f"🎉 '{title}' listed successfully! AI evaluated fair price at ${ai_val['fair_resale_price']:.2f}.", "success")
        return redirect(url_for('product_detail', product_id=new_product.id))
        
    categories = Category.query.order_by(Category.name).all()
    brands = [
        'Burberry', 'Saint Laurent', 'Gucci', 'Prada', 'Ralph Lauren',
        'Nike', 'Adidas', 'Jordan', 'Patagonia', 'Reformation',
        'Levi\'s', 'Zara', 'H&M', 'Mango', 'Other'
    ]
    return render_template('sell.html', categories=categories, brands=brands)


# =========================================================================
# 7. CHECKOUT & RENTAL BOOKING FLOW
# =========================================================================
@app.route('/checkout/<int:product_id>', methods=['GET', 'POST'])
def checkout(product_id):
    if not g.user:
        flash("Please log in to complete your transaction.", "warning")
        return redirect(url_for('login', next=request.url))
        
    product = db.session.get(Product, product_id)
    if not product or product.is_sold:
        flash("Item is unavailable or has already been purchased.", "danger")
        return redirect(url_for('marketplace'))
        
    action_type = request.args.get('type', 'buy') # 'buy' or 'rent'
    
    if request.method == 'POST':
        order_type = 'Rent' if action_type == 'rent' else 'Buy'
        shipping_address = request.form.get('shipping_address', '').strip()
        city = request.form.get('city', 'New York').strip()
        postal_code = request.form.get('postal_code', '10001').strip()
        contact_phone = request.form.get('contact_phone', '').strip()
        payment_method = request.form.get('payment_method', 'Credit Card')
        
        shipping_fee = 4.99
        order_num = f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        if order_type == 'Rent':
            start_date_str = request.form.get('start_date')
            end_date_str = request.form.get('end_date')
            
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except Exception:
                start_date = datetime.utcnow().date() + timedelta(days=2)
                end_date = start_date + timedelta(days=3)
                
            total_days = max(1, (end_date - start_date).days)
            daily_rate = product.rental_price_per_day
            rental_subtotal = round(total_days * daily_rate, 2)
            deposit = product.rental_security_deposit
            total_amount = round(rental_subtotal + deposit + shipping_fee, 2)
            
            new_order = Order(
                order_number=order_num,
                buyer_id=g.user.id,
                product_id=product.id,
                order_type='Rent',
                item_price=rental_subtotal,
                shipping_fee=shipping_fee,
                security_deposit=deposit,
                total_amount=total_amount,
                shipping_address=shipping_address,
                city=city,
                postal_code=postal_code,
                contact_phone=contact_phone,
                payment_status='Paid',
                payment_method=payment_method,
                order_status='Rental Active',
                tracking_number=f"ECO-TRK-{uuid.uuid4().hex[:8].upper()}",
                courier_partner='EcoExpress Carbon-Neutral Delivery',
                estimated_delivery=datetime.utcnow().date() + timedelta(days=2)
            )
            db.session.add(new_order)
            db.session.flush()
            
            new_booking = RentalBooking(
                order_id=new_order.id,
                product_id=product.id,
                renter_id=g.user.id,
                start_date=start_date,
                end_date=end_date,
                total_days=total_days,
                daily_rate=daily_rate,
                security_deposit=deposit,
                total_rent=rental_subtotal,
                rental_status='Active'
            )
            db.session.add(new_booking)
            product.is_currently_rented = True
            
        else: # BUY
            item_price = product.listed_price
            deposit = 0.0
            total_amount = round(item_price + shipping_fee, 2)
            
            new_order = Order(
                order_number=order_num,
                buyer_id=g.user.id,
                product_id=product.id,
                order_type='Buy',
                item_price=item_price,
                shipping_fee=shipping_fee,
                security_deposit=deposit,
                total_amount=total_amount,
                shipping_address=shipping_address,
                city=city,
                postal_code=postal_code,
                contact_phone=contact_phone,
                payment_status='Paid',
                payment_method=payment_method,
                order_status='Processing',
                tracking_number=f"ECO-TRK-{uuid.uuid4().hex[:8].upper()}",
                courier_partner='EcoShip Logistics',
                estimated_delivery=datetime.utcnow().date() + timedelta(days=3)
            )
            db.session.add(new_order)
            product.is_sold = True
            
        # Reward eco-points for sustainable pre-owned fashion purchase
        g.user.eco_points = (g.user.eco_points or 0) + 35
        
        db.session.commit()
        flash(f"🎉 Order placed successfully! Order #{order_num}", "success")
        return redirect(url_for('order_detail', order_id=new_order.id))
        
    return render_template(
        'checkout.html',
        product=product,
        action_type=action_type
    )


# =========================================================================
# 8. ORDERS, TRACKING & RETURN MANAGEMENT
# =========================================================================
@app.route('/orders')
def orders():
    if not g.user:
        flash("Please log in to view your orders.", "warning")
        return redirect(url_for('login'))
        
    user_orders = Order.query.filter_by(buyer_id=g.user.id).order_by(Order.created_at.desc()).all()
    active_rentals = [o for o in user_orders if o.order_type == 'Rent' and o.order_status in ('Rental Active', 'Processing', 'Shipped')]
    past_orders = [o for o in user_orders if o not in active_rentals]
    
    return render_template(
        'orders.html',
        active_rentals=active_rentals,
        past_orders=past_orders
    )


@app.route('/order/<int:order_id>')
def order_detail(order_id):
    if not g.user:
        flash("Please log in to view this order.", "warning")
        return redirect(url_for('login'))
        
    order = db.session.get(Order, order_id)
    if not order or (order.buyer_id != g.user.id and order.product.seller_id != g.user.id):
        flash("Order not found or unauthorized.", "danger")
        return redirect(url_for('orders'))
        
    return render_template('order_detail.html', order=order)


@app.route('/order/<int:order_id>/return', methods=['POST'])
def process_return(order_id):
    if not g.user:
        flash("Please log in.", "warning")
        return redirect(url_for('login'))
        
    order = db.session.get(Order, order_id)
    if not order or order.buyer_id != g.user.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for('orders'))
        
    reason = request.form.get('reason', 'Rental Period Complete')
    notes = request.form.get('notes', '')
    
    # Check if existing return request
    existing = ReturnRequest.query.filter_by(order_id=order.id).first()
    if existing:
        flash("Return request already exists for this order.", "info")
        return redirect(url_for('order_detail', order_id=order.id))
        
    return_type = 'Rental Return' if order.order_type == 'Rent' else 'Resale Return'
    return_req = ReturnRequest(
        order_id=order.id,
        user_id=g.user.id,
        return_type=return_type,
        reason=reason,
        notes=notes,
        status='Approved - Prepaid Return Label Ready',
        return_tracking_id=f"RET-{uuid.uuid4().hex[:8].upper()}",
        refund_amount=order.security_deposit if order.order_type == 'Rent' else order.item_price
    )
    
    order.order_status = 'Return Initiated'
    if order.rental_detail:
        order.rental_detail.rental_status = 'Return Requested'
        
    db.session.add(return_req)
    db.session.commit()
    
    flash("✅ Prepaid return shipping label generated! Courier pickup scheduled.", "success")
    return redirect(url_for('order_detail', order_id=order.id))


# =========================================================================
# 9. SELLER DASHBOARD & ANALYTICS
# =========================================================================
@app.route('/seller/dashboard')
def seller_dashboard():
    if not g.user:
        flash("Please log in to access the seller dashboard.", "warning")
        return redirect(url_for('login'))
        
    my_products = Product.query.filter_by(seller_id=g.user.id).order_by(Product.created_at.desc()).all()
    
    # Orders on seller's products
    product_ids = [p.id for p in my_products]
    seller_orders = Order.query.filter(Order.product_id.in_(product_ids)).all() if product_ids else []
    
    total_revenue = sum(o.item_price for o in seller_orders if o.payment_status == 'Paid')
    active_rentals = [o for o in seller_orders if o.order_type == 'Rent' and o.order_status == 'Rental Active']
    sold_items = [p for p in my_products if p.is_sold]
    active_listings = [p for p in my_products if not p.is_sold]
    
    # Category sales breakdown for Chart.js
    category_counts = {}
    for p in my_products:
        cat_name = p.category_rel.name if p.category_rel else 'Other'
        category_counts[cat_name] = category_counts.get(cat_name, 0) + 1
        
    return render_template(
        'seller_dashboard.html',
        my_products=my_products,
        active_listings=active_listings,
        sold_items=sold_items,
        active_rentals=active_rentals,
        total_revenue=round(total_revenue, 2),
        seller_orders=seller_orders,
        category_chart_labels=list(category_counts.keys()),
        category_chart_data=list(category_counts.values())
    )


# =========================================================================
# 10. WISHLIST & REVIEWS
# =========================================================================
@app.route('/wishlist')
def wishlist():
    if not g.user:
        flash("Please log in to view your wishlist.", "warning")
        return redirect(url_for('login'))
        
    items = Wishlist.query.filter_by(user_id=g.user.id).order_by(Wishlist.created_at.desc()).all()
    return render_template('wishlist.html', items=items)


@app.route('/api/wishlist/toggle', methods=['POST'])
def api_wishlist_toggle():
    if not g.user:
        return jsonify({'success': False, 'message': 'Please log in first'}), 401
        
    data = request.get_json() or {}
    product_id = data.get('product_id')
    
    existing = Wishlist.query.filter_by(user_id=g.user.id, product_id=product_id).first()
    if existing:
        db.session.delete(existing)
        action = 'removed'
    else:
        new_w = Wishlist(user_id=g.user.id, product_id=product_id)
        db.session.add(new_w)
        action = 'added'
        
    db.session.commit()
    total_count = Wishlist.query.filter_by(user_id=g.user.id).count()
    return jsonify({'success': True, 'action': action, 'count': total_count})


@app.route('/product/<int:product_id>/review', methods=['POST'])
def add_review(product_id):
    if not g.user:
        flash("Please log in to post a review.", "warning")
        return redirect(url_for('login'))
        
    rating = int(request.form.get('rating', 5))
    title = request.form.get('title', '').strip()
    comment = request.form.get('comment', '').strip()
    
    review = Review(
        product_id=product_id,
        user_id=g.user.id,
        rating=rating,
        title=title,
        comment=comment,
        is_verified_experience=True
    )
    db.session.add(review)
    db.session.commit()
    
    flash("🌟 Thank you for submitting your verified review!", "success")
    return redirect(url_for('product_detail', product_id=product_id))


# =========================================================================
# 11. SUSTAINABILITY & ECO IMPACT DASHBOARD
# =========================================================================
@app.route('/eco-impact')
def eco_impact():
    all_products = Product.query.all()
    total_co2 = sum(p.co2_saved_kg for p in all_products) + 850.0
    total_water = sum(p.water_saved_liters for p in all_products) + 340000.0
    items_circulated = len(all_products) + Order.query.count()
    
    user_saved_co2 = 0
    user_saved_water = 0
    if g.user:
        user_orders = Order.query.filter_by(buyer_id=g.user.id).all()
        user_saved_co2 = sum(o.product.co2_saved_kg for o in user_orders) + 18.5
        user_saved_water = sum(o.product.water_saved_liters for o in user_orders) + 7200
        
    return render_template(
        'eco_impact.html',
        total_co2=round(total_co2, 1),
        total_water=round(total_water),
        items_circulated=items_circulated,
        user_saved_co2=round(user_saved_co2, 1),
        user_saved_water=round(user_saved_water)
    )


# =========================================================================
# 12. USER AUTHENTICATION & DEMO LOGIN
# =========================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash(f"Welcome back, {user.name}!", "success")
            next_url = request.args.get('next') or url_for('marketplace')
            return redirect(next_url)
        else:
            flash("Invalid email or password. You can use the Quick Demo Logins below.", "danger")
            
    return render_template('login.html')


@app.route('/demo-login/<int:user_idx>')
def demo_login(user_idx):
    users = User.query.order_by(User.id.asc()).all()
    if 0 <= user_idx < len(users):
        user = users[user_idx]
        session['user_id'] = user.id
        flash(f"Signed in as demo user: {user.name} ({user.role.title()})", "success")
    return redirect(url_for('marketplace'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'both')
        city = request.form.get('city', 'New York').strip()
        
        if User.query.filter_by(email=email).first():
            flash("Email is already registered. Please log in.", "warning")
            return redirect(url_for('login'))
            
        new_user = User(
            name=name,
            email=email,
            role=role,
            city=city,
            profile_pic='https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80',
            eco_points=50
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        session['user_id'] = new_user.id
        flash(f"Welcome to ReWear AI, {name}! 50 Eco-Points added to your profile.", "success")
        return redirect(url_for('marketplace'))
        
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))


# =========================================================================
# APPLICATION ENTRYPOINT
# =========================================================================
if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"Notice during db.create_all(): {e}")
            
        from seed_data import seed_database
        seed_database()
        
    print("✨ ReWear AI Fashion Marketplace & Rental System is running on http://127.0.0.1:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
