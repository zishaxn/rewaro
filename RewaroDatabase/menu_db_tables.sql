-- Menu Service Database Schema

-- Categories Table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    outlet_id INTEGER NOT NULL,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_categories_outlet_id ON categories(outlet_id);

-- Menu Items Table
CREATE TABLE IF NOT EXISTS menu_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price FLOAT NOT NULL,
    image_url VARCHAR(255),
    category_id INTEGER REFERENCES categories(id),
    outlet_id INTEGER NOT NULL,
    is_vegetarian BOOLEAN DEFAULT FALSE,
    is_spicy BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_menu_items_outlet_id ON menu_items(outlet_id);
CREATE INDEX IF NOT EXISTS idx_menu_items_category_id ON menu_items(category_id);

-- Variations Table
CREATE TABLE IF NOT EXISTS variations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price_adjustment FLOAT DEFAULT 0.0,
    outlet_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_variations_outlet_id ON variations(outlet_id);

-- Addons Table
CREATE TABLE IF NOT EXISTS addons (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price FLOAT NOT NULL,
    outlet_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_addons_outlet_id ON addons(outlet_id);

-- Item-Variation Association Table
CREATE TABLE IF NOT EXISTS item_variation (
    item_id INTEGER REFERENCES menu_items(id) ON DELETE CASCADE,
    variation_id INTEGER REFERENCES variations(id) ON DELETE CASCADE,
    PRIMARY KEY (item_id, variation_id)
);

-- Item-Addon Association Table
CREATE TABLE IF NOT EXISTS item_addon (
    item_id INTEGER REFERENCES menu_items(id) ON DELETE CASCADE,
    addon_id INTEGER REFERENCES addons(id) ON DELETE CASCADE,
    PRIMARY KEY (item_id, addon_id)
);

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at columns
CREATE TRIGGER update_categories_modtime
    BEFORE UPDATE ON categories
    FOR EACH ROW
    EXECUTE PROCEDURE update_modified_column();

CREATE TRIGGER update_menu_items_modtime
    BEFORE UPDATE ON menu_items
    FOR EACH ROW
    EXECUTE PROCEDURE update_modified_column();

CREATE TRIGGER update_variations_modtime
    BEFORE UPDATE ON variations
    FOR EACH ROW
    EXECUTE PROCEDURE update_modified_column();

CREATE TRIGGER update_addons_modtime
    BEFORE UPDATE ON addons
    FOR EACH ROW
    EXECUTE PROCEDURE update_modified_column();
