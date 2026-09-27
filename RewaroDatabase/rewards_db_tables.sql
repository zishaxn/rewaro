-- Table: Central coupon configurations
CREATE TABLE coupon_configurations (
    config_id VARCHAR(20) NOT NULL,
    client_id VARCHAR(50) NOT NULL,
    coupon_category VARCHAR(20) NOT NULL,
    version_number INTEGER,
    visit_threshold INTEGER,
    discount_type VARCHAR(20),
    coupon_value VARCHAR(100),
    min_purchase VARCHAR(10),
    max_discount VARCHAR(10),
    icon_id INTEGER,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
    expires_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() + INTERVAL '90 days'),
    start_date TIMESTAMP WITHOUT TIME ZONE,
    PRIMARY KEY (config_id),
    UNIQUE (client_id, config_id),
    CONSTRAINT chk_milestone_fields CHECK (
        (coupon_category = 'MILESTONE' AND version_number IS NOT NULL AND visit_threshold IS NOT NULL) 
        OR 
        (coupon_category <> 'MILESTONE')
    )
);

-- Index for coupon_category for faster retrieval
CREATE INDEX idx_coupon_category ON coupon_configurations (coupon_category);


-- Table: Coupon terms and conditions
CREATE TABLE coupon_terms_and_conditions (
    id SERIAL PRIMARY KEY,
    terms_and_conditions TEXT NOT NULL,
    config_id VARCHAR(20) UNIQUE, -- Ensuring consistency with coupon_configurations
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT coupon_terms_and_conditions_config_id_fkey 
        FOREIGN KEY (config_id) REFERENCES coupon_configurations(config_id) ON DELETE CASCADE
);


-- Table: Coupon associations (Links phone number to coupon configuration)
CREATE TABLE coupon_associations (
    id SERIAL PRIMARY KEY,
    config_id VARCHAR(20) NOT NULL,
    client_id VARCHAR(100) NOT NULL,
    phone_no VARCHAR(15) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    CONSTRAINT fk_config FOREIGN KEY (config_id) REFERENCES coupon_configurations(config_id) ON DELETE CASCADE
);

-- Index for phone_no for faster lookup
CREATE INDEX idx_phone_no ON coupon_associations (phone_no);
ALTER TABLE coupon_associations
ADD CONSTRAINT unique_config_phone UNIQUE (config_id, phone_no);


-- Table: Customer progress tracking
CREATE TABLE customer_progress (
    progress_id SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    client_id VARCHAR(50) NOT NULL,
    config_id VARCHAR(20) NOT NULL,
    current_visits INTEGER NOT NULL DEFAULT 0,
    last_coupon_generated_at TIMESTAMP WITHOUT TIME ZONE,
    last_visit TIMESTAMP WITHOUT TIME ZONE,
    version_number INTEGER NOT NULL,
    CONSTRAINT customer_progress_config_id_fkey 
        FOREIGN KEY (config_id) REFERENCES coupon_configurations(config_id) ON DELETE CASCADE
);

-- Index for customer_id for faster retrieval
CREATE INDEX idx_customer_id ON customer_progress (customer_id);

-- Index for client_id for faster retrieval
CREATE INDEX idx_client_id ON customer_progress (client_id);


-- Table: Customer coupons
CREATE TABLE customer_coupons (
    coupon_id SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    config_id VARCHAR(20) NOT NULL,
    coupon_code VARCHAR(20) NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
    modified_on TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
    CONSTRAINT fk_config FOREIGN KEY (config_id) REFERENCES coupon_configurations(config_id) ON DELETE CASCADE
);

-- Index for customer_id in customer_coupons for faster retrieval
CREATE INDEX idx_customer_id_coupons ON customer_coupons (customer_id);
