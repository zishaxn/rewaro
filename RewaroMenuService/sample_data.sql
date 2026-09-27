-- Sample data for Menu Service
-- Run this script after schema.sql to populate the database with test data

-- Sample outlet IDs (these would normally come from your merchant_master_data table)
DO $$
DECLARE
    outlet_id_1 INT := 1001;
    outlet_id_2 INT := 1002;
BEGIN

-- Categories for Outlet 1
INSERT INTO categories (name, description, outlet_id, display_order) VALUES
('Appetizers', 'Small dishes to start your meal', outlet_id_1, 1),
('Main Course', 'Hearty entrees and signature dishes', outlet_id_1, 2),
('Desserts', 'Sweet treats to finish your meal', outlet_id_1, 3),
('Beverages', 'Refreshing drinks', outlet_id_1, 4);

-- Categories for Outlet 2
INSERT INTO categories (name, description, outlet_id, display_order) VALUES
('Breakfast', 'Start your day right', outlet_id_2, 1),
('Lunch', 'Midday favorites', outlet_id_2, 2),
('Dinner', 'Evening specialties', outlet_id_2, 3),
('Sides', 'Perfect accompaniments', outlet_id_2, 4);

-- Get IDs for the inserted categories
DECLARE
    appetizers_id INT := (SELECT id FROM categories WHERE name = 'Appetizers' AND outlet_id = outlet_id_1);
    main_course_id INT := (SELECT id FROM categories WHERE name = 'Main Course' AND outlet_id = outlet_id_1);
    desserts_id INT := (SELECT id FROM categories WHERE name = 'Desserts' AND outlet_id = outlet_id_1);
    beverages_id INT := (SELECT id FROM categories WHERE name = 'Beverages' AND outlet_id = outlet_id_1);
    breakfast_id INT := (SELECT id FROM categories WHERE name = 'Breakfast' AND outlet_id = outlet_id_2);
    lunch_id INT := (SELECT id FROM categories WHERE name = 'Lunch' AND outlet_id = outlet_id_2);
    dinner_id INT := (SELECT id FROM categories WHERE name = 'Dinner' AND outlet_id = outlet_id_2);
    sides_id INT := (SELECT id FROM categories WHERE name = 'Sides' AND outlet_id = outlet_id_2);

-- Menu Items for Outlet 1
-- Appetizers
INSERT INTO menu_items (name, description, price, category_id, outlet_id, is_vegetarian, is_spicy) VALUES
('Spring Rolls', 'Crispy rolls filled with vegetables', 6.99, appetizers_id, outlet_id_1, TRUE, FALSE),
('Buffalo Wings', 'Spicy chicken wings with blue cheese dip', 9.99, appetizers_id, outlet_id_1, FALSE, TRUE),
('Garlic Bread', 'Toasted bread with garlic butter', 4.99, appetizers_id, outlet_id_1, TRUE, FALSE);

-- Main Course
INSERT INTO menu_items (name, description, price, category_id, outlet_id, is_vegetarian, is_spicy) VALUES
('Grilled Salmon', 'Fresh salmon with lemon butter sauce', 18.99, main_course_id, outlet_id_1, FALSE, FALSE),
('Vegetable Curry', 'Mixed vegetables in a rich curry sauce', 14.99, main_course_id, outlet_id_1, TRUE, TRUE),
('Classic Burger', 'Beef patty with lettuce, tomato, and cheese', 12.99, main_course_id, outlet_id_1, FALSE, FALSE);

-- Desserts
INSERT INTO menu_items (name, description, price, category_id, outlet_id, is_vegetarian, is_spicy) VALUES
('Chocolate Cake', 'Rich chocolate layer cake', 7.99, desserts_id, outlet_id_1, TRUE, FALSE),
('Apple Pie', 'Traditional apple pie with cinnamon', 6.99, desserts_id, outlet_id_1, TRUE, FALSE);

-- Beverages
INSERT INTO menu_items (name, description, price, category_id, outlet_id, is_vegetarian, is_spicy) VALUES
('Iced Tea', 'Refreshing sweet tea with lemon', 2.99, beverages_id, outlet_id_1, TRUE, FALSE),
('Fresh Lemonade', 'Homemade lemonade', 3.99, beverages_id, outlet_id_1, TRUE, FALSE);

-- Menu Items for Outlet 2
-- Breakfast
INSERT INTO menu_items (name, description, price, category_id, outlet_id, is_vegetarian, is_spicy) VALUES
('Pancakes', 'Fluffy pancakes with maple syrup', 8.99, breakfast_id, outlet_id_2, TRUE, FALSE),
('Eggs Benedict', 'English muffin with poached eggs and hollandaise', 11.99, breakfast_id, outlet_id_2, FALSE, FALSE);

-- Lunch
INSERT INTO menu_items (name, description, price, category_id, outlet_id, is_vegetarian, is_spicy) VALUES
('Caesar Salad', 'Romaine lettuce with caesar dressing and croutons', 9.99, lunch_id, outlet_id_2, TRUE, FALSE),
('Turkey Club', 'Triple-decker sandwich with turkey and bacon', 10.99, lunch_id, outlet_id_2, FALSE, FALSE);

-- Dinner
INSERT INTO menu_items (name, description, price, category_id, outlet_id, is_vegetarian, is_spicy) VALUES
('Steak', 'Grilled ribeye with roasted potatoes', 24.99, dinner_id, outlet_id_2, FALSE, FALSE),
('Pasta Primavera', 'Pasta with seasonal vegetables', 14.99, dinner_id, outlet_id_2, TRUE, FALSE);

-- Sides
INSERT INTO menu_items (name, description, price, category_id, outlet_id, is_vegetarian, is_spicy) VALUES
('French Fries', 'Crispy golden fries', 3.99, sides_id, outlet_id_2, TRUE, FALSE),
('Coleslaw', 'Creamy cabbage slaw', 2.99, sides_id, outlet_id_2, TRUE, FALSE);

-- Variations
INSERT INTO variations (name, description, price_adjustment, outlet_id) VALUES
('Small', 'Small portion size', -2.00, outlet_id_1),
('Large', 'Large portion size', 2.00, outlet_id_1),
('Extra Spicy', 'With additional spices', 0.50, outlet_id_1),
('Gluten Free', 'Made without gluten', 1.50, outlet_id_1),
('Small', 'Small portion size', -2.00, outlet_id_2),
('Large', 'Large portion size', 2.50, outlet_id_2),
('No Salt', 'Prepared without salt', 0.00, outlet_id_2);

-- Addons
INSERT INTO addons (name, description, price, outlet_id) VALUES
('Extra Cheese', 'Additional serving of cheese', 1.50, outlet_id_1),
('Bacon', 'Crispy bacon strips', 2.00, outlet_id_1),
('Avocado', 'Fresh sliced avocado', 1.50, outlet_id_1),
('Mushrooms', 'Sautéed mushrooms', 1.00, outlet_id_1),
('Extra Sauce', 'Additional serving of sauce', 0.75, outlet_id_2),
('Cheese', 'Slice of cheese', 1.00, outlet_id_2),
('Extra Vegetables', 'Additional serving of vegetables', 1.25, outlet_id_2);

-- Item-Variation Relationships
-- For Outlet 1
INSERT INTO item_variation (item_id, variation_id)
SELECT 
    mi.id, 
    v.id
FROM 
    menu_items mi
CROSS JOIN 
    variations v
WHERE 
    mi.outlet_id = outlet_id_1 
    AND v.outlet_id = outlet_id_1
    AND mi.name IN ('Grilled Salmon', 'Vegetable Curry', 'Classic Burger')
    AND v.name IN ('Small', 'Large');

INSERT INTO item_variation (item_id, variation_id)
SELECT 
    mi.id, 
    v.id
FROM 
    menu_items mi
CROSS JOIN 
    variations v
WHERE 
    mi.outlet_id = outlet_id_1 
    AND v.outlet_id = outlet_id_1
    AND mi.name IN ('Buffalo Wings', 'Vegetable Curry')
    AND v.name IN ('Extra Spicy');

-- For Outlet 2
INSERT INTO item_variation (item_id, variation_id)
SELECT 
    mi.id, 
    v.id
FROM 
    menu_items mi
CROSS JOIN 
    variations v
WHERE 
    mi.outlet_id = outlet_id_2 
    AND v.outlet_id = outlet_id_2
    AND mi.name IN ('Pancakes', 'Pasta Primavera')
    AND v.name IN ('Small', 'Large');

INSERT INTO item_variation (item_id, variation_id)
SELECT 
    mi.id, 
    v.id
FROM 
    menu_items mi
CROSS JOIN 
    variations v
WHERE 
    mi.outlet_id = outlet_id_2 
    AND v.outlet_id = outlet_id_2
    AND mi.name IN ('French Fries', 'Coleslaw')
    AND v.name IN ('No Salt');

-- Item-Addon Relationships
-- For Outlet 1
INSERT INTO item_addon (item_id, addon_id)
SELECT 
    mi.id, 
    a.id
FROM 
    menu_items mi
CROSS JOIN 
    addons a
WHERE 
    mi.outlet_id = outlet_id_1 
    AND a.outlet_id = outlet_id_1
    AND mi.name = 'Classic Burger'
    AND a.name IN ('Extra Cheese', 'Bacon', 'Avocado');

INSERT INTO item_addon (item_id, addon_id)
SELECT 
    mi.id, 
    a.id
FROM 
    menu_items mi
CROSS JOIN 
    addons a
WHERE 
    mi.outlet_id = outlet_id_1 
    AND a.outlet_id = outlet_id_1
    AND mi.name = 'Grilled Salmon'
    AND a.name IN ('Mushrooms');

-- For Outlet 2
INSERT INTO item_addon (item_id, addon_id)
SELECT 
    mi.id, 
    a.id
FROM 
    menu_items mi
CROSS JOIN 
    addons a
WHERE 
    mi.outlet_id = outlet_id_2 
    AND a.outlet_id = outlet_id_2
    AND mi.name = 'Turkey Club'
    AND a.name IN ('Cheese', 'Extra Sauce');

INSERT INTO item_addon (item_id, addon_id)
SELECT 
    mi.id, 
    a.id
FROM 
    menu_items mi
CROSS JOIN 
    addons a
WHERE 
    mi.outlet_id = outlet_id_2 
    AND a.outlet_id = outlet_id_2
    AND mi.name = 'Pasta Primavera'
    AND a.name IN ('Extra Vegetables');

END $$;
