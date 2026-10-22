-- =========================================================================
-- ReWear AI: Pre-Owned Fashion Marketplace & Rental System
-- Complete MySQL Database Schema and Seed Data
-- =========================================================================

CREATE DATABASE IF NOT EXISTS preowned_fashion_db;
USE preowned_fashion_db;

-- 1. Users Table
DROP TABLE IF EXISTS wishlists;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS return_requests;
DROP TABLE IF EXISTS rental_bookings;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'both',
    bio TEXT,
    phone VARCHAR(20),
    address VARCHAR(255),
    city VARCHAR(100),
    profile_pic VARCHAR(255) DEFAULT 'default_avatar.jpg',
    eco_points INT DEFAULT 50,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Categories Table
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL UNIQUE,
    slug VARCHAR(80) NOT NULL UNIQUE,
    icon VARCHAR(50) DEFAULT 'bi-tag',
    description VARCHAR(255)
);

-- 3. Products Table
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    brand VARCHAR(100) NOT NULL,
    category_id INT NOT NULL,
    gender VARCHAR(20) DEFAULT 'Unisex',
    size VARCHAR(20) NOT NULL,
    color VARCHAR(50) NOT NULL,
    material VARCHAR(80) DEFAULT 'Cotton',
    original_price FLOAT NOT NULL,
    listed_price FLOAT NOT NULL,
    estimated_fair_price FLOAT,
    ai_min_price FLOAT,
    ai_max_price FLOAT,
    is_available_for_resale BOOLEAN DEFAULT TRUE,
    is_available_for_rent BOOLEAN DEFAULT TRUE,
    rental_price_per_day FLOAT DEFAULT 15.0,
    rental_security_deposit FLOAT DEFAULT 50.0,
    age_months INT DEFAULT 6,
    condition_grade VARCHAR(50) NOT NULL,
    usage_frequency VARCHAR(50) DEFAULT 'Occasionally',
    flaws_description VARCHAR(255) DEFAULT 'None. Clean & sanitized.',
    is_sold BOOLEAN DEFAULT FALSE,
    is_currently_rented BOOLEAN DEFAULT FALSE,
    primary_image VARCHAR(255) NOT NULL,
    additional_images TEXT,
    co2_saved_kg FLOAT DEFAULT 7.5,
    water_saved_liters FLOAT DEFAULT 2700.0,
    seller_id INT NOT NULL,
    views_count INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Orders Table
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(30) NOT NULL UNIQUE,
    buyer_id INT NOT NULL,
    product_id INT NOT NULL,
    order_type VARCHAR(20) DEFAULT 'Buy',
    item_price FLOAT NOT NULL,
    shipping_fee FLOAT DEFAULT 4.99,
    security_deposit FLOAT DEFAULT 0.0,
    total_amount FLOAT NOT NULL,
    shipping_address TEXT NOT NULL,
    city VARCHAR(100) DEFAULT 'New York',
    postal_code VARCHAR(20) DEFAULT '10001',
    contact_phone VARCHAR(25) NOT NULL,
    payment_status VARCHAR(30) DEFAULT 'Paid',
    payment_method VARCHAR(50) DEFAULT 'Credit Card',
    order_status VARCHAR(40) DEFAULT 'Placed',
    tracking_number VARCHAR(50),
    courier_partner VARCHAR(50) DEFAULT 'EcoExpress Logistics',
    estimated_delivery DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 5. Rental Bookings Table
CREATE TABLE rental_bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    renter_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_days INT NOT NULL DEFAULT 3,
    daily_rate FLOAT NOT NULL,
    security_deposit FLOAT NOT NULL,
    total_rent FLOAT NOT NULL,
    rental_status VARCHAR(40) DEFAULT 'Active',
    deposit_refunded BOOLEAN DEFAULT FALSE,
    return_tracking_number VARCHAR(50),
    return_notes TEXT,
    returned_at DATETIME,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (renter_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 6. Return Requests Table
CREATE TABLE return_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    user_id INT NOT NULL,
    return_type VARCHAR(30) DEFAULT 'Rental Return',
    reason VARCHAR(100) NOT NULL,
    notes TEXT,
    status VARCHAR(40) DEFAULT 'Requested',
    return_tracking_id VARCHAR(60),
    refund_amount FLOAT DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 7. Reviews Table
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT NOT NULL,
    title VARCHAR(120),
    comment TEXT NOT NULL,
    is_verified_experience BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 8. Wishlists Table
CREATE TABLE wishlists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_user_product (user_id, product_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- -------------------------------------------------------------------------
-- Seed Data Inserts
-- -------------------------------------------------------------------------

INSERT INTO categories (name, slug, icon, description) VALUES
('Jackets & Coats', 'jackets-coats', 'bi-cloud-snow', 'Trench coats, leather bikers, shearling & down jackets'),
('Dresses & Gowns', 'dresses-gowns', 'bi-stars', 'Evening wear, cocktail slips, silk gowns & gala dresses'),
('Suits & Blazers', 'suits-blazers', 'bi-briefcase', 'Tailored double-breasted blazers, tuxedos & two-piece sets'),
('Shoes & Sneakers', 'shoes-sneakers', 'bi-shoe-prints', 'Designer heels, archival boots & collector sneakers'),
('Bags & Accessories', 'bags-accessories', 'bi-handbag', 'Iconic luxury totes, crossbodies, scarves & belts'),
('Denim & Jeans', 'denim-jeans', 'bi-scissors', 'Vintage selvedge denim, straight cuts & denim jackets'),
('Sweaters & Knits', 'sweaters-knits', 'bi-feather', 'Pure cashmere knits, merino cardigans & mohair vests'),
('Ethnic Wear', 'ethnic-wear', 'bi-gem', 'Handcrafted lehengas, sherwanis, sarees & silk kurtas');

-- Demo Users (Password: 'password123')
INSERT INTO users (name, email, password_hash, role, bio, phone, city, address, profile_pic, eco_points) VALUES
('Sophia Laurent', 'sophia@example.com', 'scrypt:32768:8:1$7U60pLhGfJkU8pU8$d41d8cd98f00b204e9800998ecf8427e', 'both', 'Sustainable stylist & collector of archival luxury pieces. Circular fashion advocate.', '+1 (555) 234-5678', 'New York', '450 West 33rd Street, Manhattan', 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400', 240),
('Marcus Vance', 'marcus@example.com', 'scrypt:32768:8:1$7U60pLhGfJkU8pU8$d41d8cd98f00b204e9800998ecf8427e', 'both', 'Vintage menswear curator & designer outerwear collector. High-end streetwear enthusiast.', '+1 (555) 876-5432', 'San Francisco', '780 Mission Bay Blvd', 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400', 180),
('Elena Rostova', 'elena@example.com', 'scrypt:32768:8:1$7U60pLhGfJkU8pU8$d41d8cd98f00b204e9800998ecf8427e', 'buyer', 'Designer rental regular. Passionate about wedding guest styles & red-carpet rentals.', '+1 (555) 345-9876', 'Los Angeles', '120 Beverly Glen Blvd', 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400', 310),
('Nandni Patel', 'nandni@example.com', 'scrypt:32768:8:1$7U60pLhGfJkU8pU8$d41d8cd98f00b204e9800998ecf8427e', 'both', 'Fashion curator & researcher in AI sustainable clothing economies.', '+1 (555) 901-2345', 'Chicago', '220 N Michigan Ave', 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400', 450);
