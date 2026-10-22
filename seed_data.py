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

from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from models import db, User, Category, Product, Order, RentalBooking, ReturnRequest, Review, Wishlist
from ml_engine import price_model

def seed_database(force=False):
    print("Beginning database seeding...")
    
    # Check if already seeded
    if not force and User.query.first():
        print("Database already contains data. Skipping full re-seed.")
        return

    # 1. Create Demo Users
    users_data = [
        {
            'name': 'Sophia Laurent',
            'email': 'sophia@example.com',
            'password': 'password123',
            'role': 'both',
            'bio': 'Sustainable stylist & collector of archival luxury pieces. Circular fashion advocate.',
            'phone': '+1 (555) 234-5678',
            'city': 'New York',
            'address': '450 West 33rd Street, Manhattan',
            'profile_pic': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80',
            'eco_points': 240
        },
        {
            'name': 'Marcus Vance',
            'email': 'marcus@example.com',
            'password': 'password123',
            'role': 'both',
            'bio': 'Vintage menswear curator & designer outerwear collector. High-end streetwear enthusiast.',
            'phone': '+1 (555) 876-5432',
            'city': 'San Francisco',
            'address': '780 Mission Bay Blvd',
            'profile_pic': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=80',
            'eco_points': 180
        },
        {
            'name': 'Elena Rostova',
            'email': 'elena@example.com',
            'password': 'password123',
            'role': 'buyer',
            'bio': 'Designer rental regular. Passionate about wedding guest styles & red-carpet rentals.',
            'phone': '+1 (555) 345-9876',
            'city': 'Los Angeles',
            'address': '120 Beverly Glen Blvd',
            'profile_pic': 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&auto=format&fit=crop&q=80',
            'eco_points': 310
        },
        {
            'name': 'Nandni Patel',
            'email': 'nandni@example.com',
            'password': 'password123',
            'role': 'both',
            'bio': 'Fashion curator & researcher in AI sustainable clothing economies.',
            'phone': '+1 (555) 901-2345',
            'city': 'Chicago',
            'address': '220 N Michigan Ave',
            'profile_pic': 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&auto=format&fit=crop&q=80',
            'eco_points': 450
        }
    ]

    user_objs = []
    for u in users_data:
        usr = User(
            name=u['name'],
            email=u['email'],
            password_hash=generate_password_hash(u['password']),
            role=u['role'],
            bio=u['bio'],
            phone=u['phone'],
            city=u['city'],
            address=u['address'],
            profile_pic=u['profile_pic'],
            eco_points=u['eco_points']
        )
        db.session.add(usr)
        user_objs.append(usr)
        
    db.session.commit()
    print("Users created.")

    # 2. Create Categories
    categories_data = [
        {'name': 'Jackets & Coats', 'slug': 'jackets-coats', 'icon': 'bi-cloud-snow', 'description': 'Trench coats, leather bikers, shearling & down jackets'},
        {'name': 'Dresses & Gowns', 'slug': 'dresses-gowns', 'icon': 'bi-stars', 'description': 'Evening wear, cocktail slips, silk gowns & gala dresses'},
        {'name': 'Suits & Blazers', 'slug': 'suits-blazers', 'icon': 'bi-briefcase', 'description': 'Tailored double-breasted blazers, tuxedos & two-piece sets'},
        {'name': 'Shoes & Sneakers', 'slug': 'shoes-sneakers', 'icon': 'bi-shoe-prints', 'description': 'Designer heels, archival boots & collector sneakers'},
        {'name': 'Bags & Accessories', 'slug': 'bags-accessories', 'icon': 'bi-handbag', 'description': 'Iconic luxury totes, crossbodies, scarves & belts'},
        {'name': 'Denim & Jeans', 'slug': 'denim-jeans', 'icon': 'bi-scissors', 'description': 'Vintage selvedge denim, straight cuts & denim jackets'},
        {'name': 'Sweaters & Knits', 'slug': 'sweaters-knits', 'icon': 'bi-feather', 'description': 'Pure cashmere knits, merino cardigans & mohair vests'},
        {'name': 'Ethnic Wear', 'slug': 'ethnic-wear', 'icon': 'bi-gem', 'description': 'Handcrafted lehengas, sherwanis, sarees & silk kurtas'}
    ]

    cat_map = {}
    for c in categories_data:
        cat = Category(
            name=c['name'],
            slug=c['slug'],
            icon=c['icon'],
            description=c['description']
        )
        db.session.add(cat)
        db.session.flush()
        cat_map[c['name']] = cat.id

    db.session.commit()
    print("Categories created.")

    # 3. Create Realistic Pre-Owned & Rental Fashion Catalog
    products_data = [
        {
            'title': 'Burberry Classic Kensington Double-Breasted Trench Coat',
            'brand': 'Burberry',
            'category': 'Jackets & Coats',
            'gender': 'Women',
            'size': 'M',
            'color': 'Honey Beige',
            'material': 'Cotton Gabardine',
            'original_price': 2490.0,
            'listed_price': 895.0, # Great Deal
            'age_months': 14,
            'condition': 'Like New',
            'usage_frequency': 'Rarely',
            'flaws_description': 'Flawless condition. Worn twice for photoshoot, dry-cleaned.',
            'is_available_for_resale': True,
            'is_available_for_rent': True,
            'rental_price_per_day': 38.0,
            'rental_security_deposit': 150.0,
            'primary_image': 'https://images.unsplash.com/photo-1544441893-675973e31985?w=800&auto=format&fit=crop&q=80',
            'seller_index': 0,
            'description': 'The quintessential British heritage trench coat. Crafted in England from weatherproof cotton gabardine with signature vintage check lining, horn buttons, and buckle collar.'
        },
        {
            'title': 'Saint Laurent L01 Vintage Black Lambskin Biker Jacket',
            'brand': 'Saint Laurent',
            'category': 'Jackets & Coats',
            'gender': 'Men',
            'size': 'L',
            'color': 'Jet Black',
            'material': 'Leather',
            'original_price': 4990.0,
            'listed_price': 2250.0,
            'age_months': 22,
            'condition': 'Gently Used',
            'usage_frequency': 'Occasionally',
            'flaws_description': 'Beautiful natural leather patina. No tears, zippers 100% functional.',
            'is_available_for_resale': True,
            'is_available_for_rent': True,
            'rental_price_per_day': 65.0,
            'rental_security_deposit': 300.0,
            'primary_image': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&auto=format&fit=crop&q=80',
            'seller_index': 1,
            'description': 'The holy grail of rock-and-roll luxury outerwear designed by Hedi Slimane. Heavyweight buttery calfskin with silver-tone hardware, shoulder epaulets, and multiple asymmetric zip pockets.'
        },
        {
            'title': 'Prada Re-Nylon Monolith Lug-Sole Combat Boots',
            'brand': 'Prada',
            'category': 'Shoes & Sneakers',
            'gender': 'Unisex',
            'size': 'M',
            'color': 'Black',
            'material': 'Leather',
            'original_price': 1650.0,
            'listed_price': 720.0,
            'age_months': 8,
            'condition': 'Like New',
            'usage_frequency': 'Rarely',
            'flaws_description': 'Original box and dust bags included. Very light sole scuffs.',
            'is_available_for_resale': True,
            'is_available_for_rent': True,
            'rental_price_per_day': 28.0,
            'rental_security_deposit': 100.0,
            'primary_image': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&auto=format&fit=crop&q=80',
            'seller_index': 3,
            'description': 'Chunky lug-sole combat boots featuring Prada\'s sustainable Re-Nylon and brushed leather with detachable branded ankle pouches.'
        },
        {
            'title': 'Reformation Winslow Wrap Maxi Dress in Emerald Silk',
            'brand': 'Reformation',
            'category': 'Dresses & Gowns',
            'gender': 'Women',
            'size': 'S',
            'color': 'Emerald Green',
            'material': 'Silk',
            'original_price': 348.0,
            'listed_price': 145.0,
            'age_months': 6,
            'condition': 'Brand New with Tags',
            'usage_frequency': 'Rarely',
            'flaws_description': 'Unworn with original Reformation tags attached.',
            'is_available_for_resale': True,
            'is_available_for_rent': True,
            'rental_price_per_day': 18.0,
            'rental_security_deposit': 45.0,
            'primary_image': 'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=800&auto=format&fit=crop&q=80',
            'seller_index': 0,
            'description': 'A sweeping kimono-sleeve maxi dress that wraps at the waist. Beautiful draped silhouette perfect for black tie, weddings, and evening galas.'
        },
        {
            'title': 'Ralph Lauren Purple Label Handmade Cashmere Turtleneck',
            'brand': 'Ralph Lauren',
            'category': 'Sweaters & Knits',
            'gender': 'Men',
            'size': 'XL',
            'color': 'Heather Oatmeal',
            'material': 'Cashmere',
            'original_price': 1295.0,
            'listed_price': 420.0,
            'age_months': 16,
            'condition': 'Gently Used',
            'usage_frequency': 'Occasionally',
            'flaws_description': 'Zero pilling. Always stored in cedar garment pouch with lavender.',
            'is_available_for_resale': True,
            'is_available_for_rent': False,
            'rental_price_per_day': 22.0,
            'rental_security_deposit': 80.0,
            'primary_image': 'https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=800&auto=format&fit=crop&q=80',
            'seller_index': 1,
            'description': 'Artisanal Italian knitwear from Ralph Lauren\'s flagship Purple Label. 100% Scottish two-ply cashmere with rich ribbed cuffs and roll neck collar.'
        },
        {
            'title': 'Gucci 1955 Horsebit Shoulder Bag in GG Supreme Canvas',
            'brand': 'Gucci',
            'category': 'Bags & Accessories',
            'gender': 'Women',
            'size': 'Free Size',
            'color': 'Beige / Ebony',
            'material': 'Leather',
            'original_price': 3200.0,
            'listed_price': 1850.0,
            'age_months': 11,
            'condition': 'Like New',
            'usage_frequency': 'Rarely',
            'flaws_description': 'Includes authentication certificate, original dustbag and retail box.',
            'is_available_for_resale': True,
            'is_available_for_rent': True,
            'rental_price_per_day': 45.0,
            'rental_security_deposit': 250.0,
            'primary_image': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=800&auto=format&fit=crop&q=80',
            'seller_index': 0,
            'description': 'Recreated from an archival 1955 design. Combines original details first introduced over six decades ago with a modern spirit, highlighting the signature gold horsebit hardware.'
        },
        {
            'title': 'Levi\'s Vintage Clothing 1947 501 Selvedge Raw Jeans',
            'brand': 'Levi\'s',
            'category': 'Denim & Jeans',
            'gender': 'Men',
            'size': 'M',
            'color': 'Indigo Dark Wash',
            'material': 'Denim',
            'original_price': 260.0,
            'listed_price': 115.0,
            'age_months': 9,
            'condition': 'Like New',
            'usage_frequency': 'Rarely',
            'flaws_description': 'Unwashed raw Cone Mills White Oak selvedge denim. Crisp seams.',
            'is_available_for_resale': True,
            'is_available_for_rent': False,
            'rental_price_per_day': 12.0,
            'rental_security_deposit': 30.0,
            'primary_image': 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800&auto=format&fit=crop&q=80',
            'seller_index': 1,
            'description': 'An exact replica of the postwar 1947 501 jeans. Features hidden rivets on back pockets, Big E red tab, and red selvedge line woven on shuttle looms.'
        },
        {
            'title': 'Zara Limited Edition Double Breasted Wool Blazer',
            'brand': 'Zara',
            'category': 'Suits & Blazers',
            'gender': 'Women',
            'size': 'M',
            'color': 'Charcoal Houndstooth',
            'material': 'Wool',
            'original_price': 169.0,
            'listed_price': 65.0,
            'age_months': 5,
            'condition': 'Like New',
            'usage_frequency': 'Occasionally',
            'flaws_description': 'Like new, no pulls or odors. Modern oversized structured shoulder silhouette.',
            'is_available_for_resale': True,
            'is_available_for_rent': True,
            'rental_price_per_day': 12.0,
            'rental_security_deposit': 25.0,
            'primary_image': 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800&auto=format&fit=crop&q=80',
            'seller_index': 3,
            'description': 'Structured blazer made of Manteco Italian wool blend. Peaked lapels, shoulder pads, front flap pockets, and tort back button fastening.'
        },
        {
            'title': 'Patagonia Retro-X Deep Pile Fleece Jacket',
            'brand': 'Patagonia',
            'category': 'Jackets & Coats',
            'gender': 'Unisex',
            'size': 'L',
            'color': 'Natural Cream / Navy',
            'material': 'Polyester',
            'original_price': 229.0,
            'listed_price': 130.0,
            'age_months': 10,
            'condition': 'Gently Used',
            'usage_frequency': 'Occasionally',
            'flaws_description': 'Very clean. Fleece is fluffy with no matted elbows.',
            'is_available_for_resale': True,
            'is_available_for_rent': False,
            'rental_price_per_day': 14.0,
            'rental_security_deposit': 35.0,
            'primary_image': 'https://images.unsplash.com/photo-1578587018452-892bacefd3f2?w=800&auto=format&fit=crop&q=80',
            'seller_index': 1,
            'description': 'Windproof, warm bonded sherpa fleece jacket made with 85% recycled polyester. Fair Trade Certified sewn with vertical zip chest pocket.'
        },
        {
            'title': 'Sabyasachi Heritage Silk Organza Embroidered Lehenga Set',
            'brand': 'Other',
            'category': 'Ethnic Wear',
            'gender': 'Women',
            'size': 'M',
            'color': 'Dusty Rose & Antique Gold',
            'material': 'Silk',
            'original_price': 3800.0,
            'listed_price': 1650.0,
            'age_months': 12,
            'condition': 'Like New',
            'usage_frequency': 'Rarely',
            'flaws_description': 'Worn once for a 4-hour indoor reception. Pristine zardozi work.',
            'is_available_for_resale': True,
            'is_available_for_rent': True,
            'rental_price_per_day': 85.0,
            'rental_security_deposit': 350.0,
            'primary_image': 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&auto=format&fit=crop&q=80',
            'seller_index': 3,
            'description': 'Handcrafted pure mulberry silk organza lehenga embellished with delicate marodi and tilla embroidery. Complete 3-piece set including blouse, can-can skirt, and sheer veil.'
        },
        {
            'title': 'Nike Air Jordan 1 Retro High OG Chicago Lost & Found',
            'brand': 'Jordan',
            'category': 'Shoes & Sneakers',
            'gender': 'Men',
            'size': 'L',
            'color': 'Varsity Red / White / Black',
            'material': 'Leather',
            'original_price': 180.0,
            'listed_price': 310.0, # Collectible resale
            'age_months': 18,
            'condition': 'Brand New with Tags',
            'usage_frequency': 'Rarely',
            'flaws_description': 'Deadstock in original box with retro sales receipt and tissue paper.',
            'is_available_for_resale': True,
            'is_available_for_rent': False,
            'rental_price_per_day': 25.0,
            'rental_security_deposit': 100.0,
            'primary_image': 'https://images.unsplash.com/photo-1552346154-21d32810aba3?w=800&auto=format&fit=crop&q=80',
            'seller_index': 1,
            'description': 'Iconic 1985 Chicago colorway tribute. Features cracked leather collars, vintage sail midsoles, and authentic archival packaging details.'
        },
        {
            'title': 'Hugo Boss Slim Fit Virgin Wool Tuxedo Two-Piece',
            'brand': 'Ralph Lauren',
            'category': 'Suits & Blazers',
            'gender': 'Men',
            'size': 'L',
            'color': 'Midnight Navy',
            'material': 'Wool',
            'original_price': 995.0,
            'listed_price': 360.0,
            'age_months': 15,
            'condition': 'Like New',
            'usage_frequency': 'Rarely',
            'flaws_description': 'Silk satin lapels are immaculate. Trousers hemmed for 32" inseam.',
            'is_available_for_resale': True,
            'is_available_for_rent': True,
            'rental_price_per_day': 40.0,
            'rental_security_deposit': 120.0,
            'primary_image': 'https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800&auto=format&fit=crop&q=80',
            'seller_index': 1,
            'description': 'Sharp evening tuxedo crafted in pure virgin wool with refined satin shawl lapels. Ideal for galas, black-tie celebrations, and weddings.'
        }
    ]

    prod_objs = []
    for p in products_data:
        cat_id = cat_map[p['category']]
        seller = user_objs[p['seller_index']]
        
        # Calculate AI fair valuation dynamically with the trained model
        ai_val = price_model.predict_fair_price(
            brand=p['brand'],
            category=p['category'],
            original_price=p['original_price'],
            age_months=p['age_months'],
            condition=p['condition'],
            usage_frequency=p['usage_frequency'],
            material=p['material']
        )
        
        prod = Product(
            title=p['title'],
            description=p['description'],
            brand=p['brand'],
            category_id=cat_id,
            gender=p['gender'],
            size=p['size'],
            color=p['color'],
            material=p['material'],
            original_price=p['original_price'],
            listed_price=p['listed_price'],
            estimated_fair_price=ai_val['fair_resale_price'],
            ai_min_price=ai_val['min_price'],
            ai_max_price=ai_val['max_price'],
            is_available_for_resale=p['is_available_for_resale'],
            is_available_for_rent=p['is_available_for_rent'],
            rental_price_per_day=p['rental_price_per_day'],
            rental_security_deposit=p['rental_security_deposit'],
            age_months=p['age_months'],
            condition=p['condition'],
            usage_frequency=p['usage_frequency'],
            flaws_description=p['flaws_description'],
            primary_image=p['primary_image'],
            co2_saved_kg=ai_val['co2_saved_kg'],
            water_saved_liters=ai_val['water_saved_liters'],
            seller_id=seller.id,
            views_count=142
        )
        db.session.add(prod)
        prod_objs.append(prod)

    db.session.commit()
    print(f"Products seeded: {len(prod_objs)} fashion pieces.")

    # 4. Create Sample Reviews
    reviews_data = [
        {
            'product_idx': 0, # Burberry Trench
            'user_idx': 2,    # Elena
            'rating': 5,
            'title': 'Better than retail condition!',
            'comment': 'The AI fair price indicator was spot on. I rented this trench coat for London Fashion Week and received compliments everywhere. Smelled like fresh cedar, totally spotless.'
        },
        {
            'product_idx': 0,
            'user_idx': 1,    # Marcus
            'rating': 5,
            'title': 'True luxury piece',
            'comment': 'The fabric weight is unmistakable authentic gabardine. Seamless rental booking and return logistics.'
        },
        {
            'product_idx': 1, # Saint Laurent Biker
            'user_idx': 2,
            'rating': 5,
            'title': 'Iconic piece of fashion history',
            'comment': 'Purchased with confidence because the AI valuation explained why the resale value stays so high. Exactly as photographed.'
        },
        {
            'product_idx': 3, # Reformation Dress
            'user_idx': 3,    # Nandni
            'rating': 5,
            'title': 'Stunning wedding guest look',
            'comment': 'Rented for 4 days. The security deposit was refunded within 24 hours of inspection. Circular fashion at its absolute best!'
        },
        {
            'product_idx': 5, # Gucci Bag
            'user_idx': 2,
            'rating': 5,
            'title': 'Unmatched elegance & verified authentic',
            'comment': 'I compared 3 bags on the comparison tool before buying this. The deal badge showed it was 30% below average market price, and it arrived in mint condition.'
        }
    ]

    for r in reviews_data:
        rev = Review(
            product_id=prod_objs[r['product_idx']].id,
            user_id=user_objs[r['user_idx']].id,
            rating=r['rating'],
            title=r['title'],
            comment=r['comment'],
            is_verified_experience=True,
            created_at=datetime.utcnow() - timedelta(days=5)
        )
        db.session.add(rev)

    # 5. Create Sample Orders & Rental Bookings
    order1 = Order(
        order_number='ORD-2026-98124',
        buyer_id=user_objs[2].id, # Elena
        product_id=prod_objs[0].id, # Burberry
        order_type='Rent',
        item_price=114.0, # 3 days @ 38
        shipping_fee=4.99,
        security_deposit=150.0,
        total_amount=268.99,
        shipping_address='120 Beverly Glen Blvd',
        city='Los Angeles',
        postal_code='90024',
        contact_phone='+1 (555) 345-9876',
        payment_status='Paid',
        payment_method='Credit Card (Visa ending in 4242)',
        order_status='Rental Active',
        tracking_number='ECO-TRK-7712093',
        courier_partner='EcoShip Carbon-Neutral Courier',
        estimated_delivery=(datetime.utcnow() + timedelta(days=1)).date(),
        created_at=datetime.utcnow() - timedelta(days=2)
    )
    db.session.add(order1)
    db.session.flush()

    booking1 = RentalBooking(
        order_id=order1.id,
        product_id=prod_objs[0].id,
        renter_id=user_objs[2].id,
        start_date=(datetime.utcnow() - timedelta(days=1)).date(),
        end_date=(datetime.utcnow() + timedelta(days=3)).date(),
        total_days=4,
        daily_rate=38.0,
        security_deposit=150.0,
        total_rent=152.0,
        rental_status='Active',
        deposit_refunded=False
    )
    db.session.add(booking1)

    # Order 2: Buy order
    order2 = Order(
        order_number='ORD-2026-77401',
        buyer_id=user_objs[3].id, # Nandni
        product_id=prod_objs[7].id, # Zara Blazer
        order_type='Buy',
        item_price=65.0,
        shipping_fee=4.99,
        security_deposit=0.0,
        total_amount=69.99,
        shipping_address='220 N Michigan Ave',
        city='Chicago',
        postal_code='60601',
        contact_phone='+1 (555) 901-2345',
        payment_status='Paid',
        payment_method='Apple Pay',
        order_status='Delivered',
        tracking_number='ECO-TRK-9901431',
        courier_partner='EcoExpress Logistics',
        estimated_delivery=(datetime.utcnow() - timedelta(days=1)).date(),
        created_at=datetime.utcnow() - timedelta(days=6)
    )
    db.session.add(order2)

    # Wishlist initial items
    wl1 = Wishlist(user_id=user_objs[0].id, product_id=prod_objs[5].id) # Gucci bag
    wl2 = Wishlist(user_id=user_objs[0].id, product_id=prod_objs[1].id) # Biker
    wl3 = Wishlist(user_id=user_objs[2].id, product_id=prod_objs[3].id) # Reformation
    db.session.add_all([wl1, wl2, wl3])

    db.session.commit()
    print("Database seeding completed successfully!")

if __name__ == '__main__':
    from app import app
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"Notice during db.create_all(): {e}")
        force = '--reset' in sys.argv or '--force' in sys.argv
        if force:
            print("Resetting existing database records...")
            db.drop_all()
            db.create_all()
        seed_database(force=force)
