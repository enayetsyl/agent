-- ============================================
-- Agent 1: Sample Data Seeding Script
-- ============================================
-- This file contains sample data for testing
-- and development purposes.
-- ============================================

-- Clear existing data (in reverse order of dependencies)
TRUNCATE TABLE product_reviews CASCADE;
TRUNCATE TABLE product_tag_relations CASCADE;
TRUNCATE TABLE product_tags CASCADE;
TRUNCATE TABLE product_images CASCADE;
TRUNCATE TABLE variant_attributes CASCADE;
TRUNCATE TABLE product_variants CASCADE;
TRUNCATE TABLE products CASCADE;
TRUNCATE TABLE categories CASCADE;

-- Reset sequences
ALTER SEQUENCE categories_id_seq RESTART WITH 1;
ALTER SEQUENCE products_id_seq RESTART WITH 1;
ALTER SEQUENCE product_variants_id_seq RESTART WITH 1;
ALTER SEQUENCE variant_attributes_id_seq RESTART WITH 1;
ALTER SEQUENCE product_images_id_seq RESTART WITH 1;
ALTER SEQUENCE product_tags_id_seq RESTART WITH 1;
ALTER SEQUENCE product_reviews_id_seq RESTART WITH 1;

-- ============================================
-- Insert Categories
-- ============================================

INSERT INTO categories (name, slug, description) VALUES
('Apparel', 'apparel', 'Clothing and accessories'),
('Electronics', 'electronics', 'Electronic devices and gadgets'),
('Footwear', 'footwear', 'Shoes and boots'),
('Home & Garden', 'home-garden', 'Home improvement and garden supplies'),
('Sports & Outdoors', 'sports-outdoors', 'Sports equipment and outdoor gear'),
('Books & Media', 'books-media', 'Books, movies, and music');

-- ============================================
-- Insert Products
-- ============================================

INSERT INTO products (name, slug, description, short_description, sku, price, compare_at_price, category_id, brand, status, featured) VALUES
('Red Cotton T-Shirt', 'red-cotton-tshirt', 'Comfortable 100% cotton t-shirt, perfect for everyday wear. Available in multiple sizes and colors. Machine washable.', 'Comfortable cotton t-shirt', 'TSH-RED-001', 29.99, 39.99, 1, 'BasicWear', 'active', true),
('Blue Denim Jeans', 'blue-denim-jeans', 'Classic fit denim jeans with stretch comfort. Durable construction with reinforced seams. Perfect for casual wear.', 'Classic fit jeans', 'JNS-BLU-001', 79.99, 99.99, 1, 'DenimCo', 'active', true),
('Wireless Headphones', 'wireless-headphones', 'Premium noise-cancelling wireless headphones with 30-hour battery life. Bluetooth 5.0 connectivity. Comfortable over-ear design.', 'Noise-cancelling headphones', 'HD-WLS-001', 149.99, 199.99, 2, 'AudioTech', 'active', true),
('Running Shoes', 'running-shoes', 'Lightweight running shoes with cushioned sole and breathable mesh upper. Perfect for daily runs and workouts.', 'Lightweight running shoes', 'SHO-RUN-001', 89.99, 119.99, 3, 'RunFast', 'active', true),
('Garden Tool Set', 'garden-tool-set', 'Complete 5-piece garden tool set including trowel, pruner, weeder, cultivator, and gloves. Durable stainless steel construction.', '5-piece garden tool set', 'GAR-SET-001', 49.99, NULL, 4, 'GardenPro', 'active', false),
('Yoga Mat', 'yoga-mat', 'Non-slip yoga mat with extra cushioning. Eco-friendly material. Includes carrying strap.', 'Non-slip yoga mat', 'SPT-YOG-001', 34.99, 44.99, 5, 'ZenFit', 'active', true),
('Programming Book: TypeScript Guide', 'typescript-guide-book', 'Comprehensive guide to TypeScript programming. Covers advanced topics and best practices. 500+ pages.', 'TypeScript programming guide', 'BOK-TYP-001', 39.99, NULL, 6, 'TechBooks', 'active', false),
('Black Leather Jacket', 'black-leather-jacket', 'Classic black leather jacket with quilted lining. Genuine leather exterior. Available in sizes S-XL.', 'Classic leather jacket', 'JKT-BLK-001', 199.99, 249.99, 1, 'LeatherCraft', 'active', true),
('Smart Watch', 'smart-watch', 'Feature-rich smartwatch with heart rate monitor, GPS, and 7-day battery life. Water-resistant up to 50m.', 'Feature-rich smartwatch', 'WCH-SMT-001', 179.99, 229.99, 2, 'TechWear', 'active', true),
('Hiking Boots', 'hiking-boots', 'Waterproof hiking boots with ankle support. Vibram sole for excellent traction. Suitable for all terrains.', 'Waterproof hiking boots', 'SHO-HIK-001', 129.99, 159.99, 3, 'TrailMaster', 'active', false);

-- ============================================
-- Insert Product Variants
-- ============================================

-- Red Cotton T-Shirt variants
INSERT INTO product_variants (product_id, name, sku, price, stock_quantity, track_inventory) VALUES
(1, 'Size: S, Color: Red', 'TSH-RED-001-S-RED', 29.99, 50, true),
(1, 'Size: M, Color: Red', 'TSH-RED-001-M-RED', 29.99, 75, true),
(1, 'Size: L, Color: Red', 'TSH-RED-001-L-RED', 29.99, 60, true),
(1, 'Size: XL, Color: Red', 'TSH-RED-001-XL-RED', 29.99, 40, true);

-- Blue Denim Jeans variants
INSERT INTO product_variants (product_id, name, sku, price, stock_quantity, track_inventory) VALUES
(2, 'Size: 30x32', 'JNS-BLU-001-30-32', 79.99, 25, true),
(2, 'Size: 32x32', 'JNS-BLU-001-32-32', 79.99, 30, true),
(2, 'Size: 34x32', 'JNS-BLU-001-34-32', 79.99, 20, true),
(2, 'Size: 36x32', 'JNS-BLU-001-36-32', 79.99, 15, true);

-- Wireless Headphones (no variants, single product)
INSERT INTO product_variants (product_id, name, sku, price, stock_quantity, track_inventory) VALUES
(3, 'Standard', 'HD-WLS-001-STD', 149.99, 100, true);

-- Running Shoes variants
INSERT INTO product_variants (product_id, name, sku, price, stock_quantity, track_inventory) VALUES
(4, 'Size: 8, Color: Black', 'SHO-RUN-001-8-BLK', 89.99, 30, true),
(4, 'Size: 9, Color: Black', 'SHO-RUN-001-9-BLK', 89.99, 35, true),
(4, 'Size: 10, Color: Black', 'SHO-RUN-001-10-BLK', 89.99, 40, true),
(4, 'Size: 11, Color: Black', 'SHO-RUN-001-11-BLK', 89.99, 25, true),
(4, 'Size: 9, Color: White', 'SHO-RUN-001-9-WHT', 89.99, 20, true),
(4, 'Size: 10, Color: White', 'SHO-RUN-001-10-WHT', 89.99, 22, true);

-- Garden Tool Set (no variants)
INSERT INTO product_variants (product_id, name, sku, price, stock_quantity, track_inventory) VALUES
(5, 'Standard Set', 'GAR-SET-001-STD', 49.99, 50, true);

-- Yoga Mat (no variants)
INSERT INTO product_variants (product_id, name, sku, price, stock_quantity, track_inventory) VALUES
(6, 'Standard', 'SPT-YOG-001-STD', 34.99, 80, true);

-- Programming Book (no variants)
INSERT INTO product_variants (product_id, name, sku, price, stock_quantity, track_inventory) VALUES
(7, 'Paperback', 'BOK-TYP-001-PBK', 39.99, 15, true);

-- Black Leather Jacket variants
INSERT INTO product_variants (product_id, name, sku, price, stock_quantity, track_inventory) VALUES
(8, 'Size: S', 'JKT-BLK-001-S', 199.99, 10, true),
(8, 'Size: M', 'JKT-BLK-001-M', 199.99, 12, true),
(8, 'Size: L', 'JKT-BLK-001-L', 199.99, 8, true),
(8, 'Size: XL', 'JKT-BLK-001-XL', 199.99, 5, true);

-- Smart Watch (no variants)
INSERT INTO product_variants (product_id, name, sku, price, stock_quantity, track_inventory) VALUES
(9, 'Standard', 'WCH-SMT-001-STD', 179.99, 60, true);

-- Hiking Boots variants
INSERT INTO product_variants (product_id, name, sku, price, stock_quantity, track_inventory) VALUES
(10, 'Size: 8', 'SHO-HIK-001-8', 129.99, 18, true),
(10, 'Size: 9', 'SHO-HIK-001-9', 129.99, 20, true),
(10, 'Size: 10', 'SHO-HIK-001-10', 129.99, 22, true),
(10, 'Size: 11', 'SHO-HIK-001-11', 129.99, 15, true);

-- ============================================
-- Insert Variant Attributes
-- ============================================

-- Red Cotton T-Shirt attributes
INSERT INTO variant_attributes (variant_id, attribute_name, attribute_value) VALUES
(1, 'size', 'S'), (1, 'color', 'Red'),
(2, 'size', 'M'), (2, 'color', 'Red'),
(3, 'size', 'L'), (3, 'color', 'Red'),
(4, 'size', 'XL'), (4, 'color', 'Red');

-- Blue Denim Jeans attributes
INSERT INTO variant_attributes (variant_id, attribute_name, attribute_value) VALUES
(5, 'waist', '30'), (5, 'inseam', '32'),
(6, 'waist', '32'), (6, 'inseam', '32'),
(7, 'waist', '34'), (7, 'inseam', '32'),
(8, 'waist', '36'), (8, 'inseam', '32');

-- Running Shoes attributes
INSERT INTO variant_attributes (variant_id, attribute_name, attribute_value) VALUES
(11, 'size', '8'), (11, 'color', 'Black'),
(12, 'size', '9'), (12, 'color', 'Black'),
(13, 'size', '10'), (13, 'color', 'Black'),
(14, 'size', '11'), (14, 'color', 'Black'),
(15, 'size', '9'), (15, 'color', 'White'),
(16, 'size', '10'), (16, 'color', 'White');

-- Black Leather Jacket attributes
INSERT INTO variant_attributes (variant_id, attribute_name, attribute_value) VALUES
(19, 'size', 'S'),
(20, 'size', 'M'),
(21, 'size', 'L'),
(22, 'size', 'XL');

-- Hiking Boots attributes
INSERT INTO variant_attributes (variant_id, attribute_name, attribute_value) VALUES
(24, 'size', '8'),
(25, 'size', '9'),
(26, 'size', '10'),
(27, 'size', '11');

-- ============================================
-- Insert Product Images
-- ============================================

INSERT INTO product_images (product_id, variant_id, url, alt_text, sort_order, is_primary) VALUES
(1, NULL, 'https://via.placeholder.com/800x800?text=Red+Cotton+T-Shirt', 'Red Cotton T-Shirt', 1, true),
(2, NULL, 'https://via.placeholder.com/800x800?text=Blue+Denim+Jeans', 'Blue Denim Jeans', 1, true),
(3, NULL, 'https://via.placeholder.com/800x800?text=Wireless+Headphones', 'Wireless Headphones', 1, true),
(4, NULL, 'https://via.placeholder.com/800x800?text=Running+Shoes', 'Running Shoes', 1, true),
(5, NULL, 'https://via.placeholder.com/800x800?text=Garden+Tool+Set', 'Garden Tool Set', 1, true),
(6, NULL, 'https://via.placeholder.com/800x800?text=Yoga+Mat', 'Yoga Mat', 1, true),
(7, NULL, 'https://via.placeholder.com/800x800?text=TypeScript+Guide+Book', 'TypeScript Guide Book', 1, true),
(8, NULL, 'https://via.placeholder.com/800x800?text=Black+Leather+Jacket', 'Black Leather Jacket', 1, true),
(9, NULL, 'https://via.placeholder.com/800x800?text=Smart+Watch', 'Smart Watch', 1, true),
(10, NULL, 'https://via.placeholder.com/800x800?text=Hiking+Boots', 'Hiking Boots', 1, true);

-- ============================================
-- Insert Product Tags
-- ============================================

INSERT INTO product_tags (name, slug) VALUES
('New Arrival', 'new-arrival'),
('Best Seller', 'best-seller'),
('Sale', 'sale'),
('Eco-Friendly', 'eco-friendly'),
('Premium', 'premium'),
('Casual', 'casual'),
('Sportswear', 'sportswear'),
('Accessories', 'accessories');

-- ============================================
-- Insert Product Tag Relations
-- ============================================

INSERT INTO product_tag_relations (product_id, tag_id) VALUES
(1, 1), -- Red T-Shirt: New Arrival
(1, 6), -- Red T-Shirt: Casual
(2, 2), -- Blue Jeans: Best Seller
(2, 6), -- Blue Jeans: Casual
(3, 2), -- Headphones: Best Seller
(3, 5), -- Headphones: Premium
(4, 7), -- Running Shoes: Sportswear
(6, 4), -- Yoga Mat: Eco-Friendly
(6, 7), -- Yoga Mat: Sportswear
(8, 5), -- Leather Jacket: Premium
(9, 1), -- Smart Watch: New Arrival
(9, 5); -- Smart Watch: Premium

-- ============================================
-- Insert Product Reviews
-- ============================================

INSERT INTO product_reviews (product_id, user_id, rating, title, review_text, verified_purchase, helpful_count) VALUES
(1, 1, 5, 'Great quality!', 'Love this t-shirt. Very comfortable and fits perfectly.', true, 12),
(1, 2, 4, 'Good value', 'Nice shirt for the price. Material is soft.', true, 8),
(2, 1, 5, 'Perfect fit', 'These jeans fit great and are very comfortable. Highly recommend!', true, 15),
(3, 3, 5, 'Excellent sound quality', 'Best headphones I have ever owned. Battery life is amazing!', true, 23),
(3, 4, 4, 'Good but could be better', 'Sound is great but the ear cups could be more comfortable.', true, 5),
(4, 2, 5, 'Great running shoes', 'Lightweight and comfortable. Perfect for my daily runs.', true, 18),
(6, 5, 5, 'Perfect yoga mat', 'Non-slip surface works great. Very happy with this purchase.', true, 10),
(9, 3, 4, 'Feature-rich watch', 'Lots of features and good battery life. GPS is accurate.', true, 14);

-- ============================================
-- Verification Queries (Optional - for testing)
-- ============================================

-- Uncomment to verify data insertion:
-- SELECT COUNT(*) as category_count FROM categories;
-- SELECT COUNT(*) as product_count FROM products;
-- SELECT COUNT(*) as variant_count FROM product_variants;
-- SELECT COUNT(*) as review_count FROM product_reviews;

