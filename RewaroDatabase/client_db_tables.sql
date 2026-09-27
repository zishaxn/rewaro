-- Table: client_master_table
CREATE TABLE client_master_table (
    client_id VARCHAR(50) NOT NULL,
    phone_no VARCHAR(15),
    email VARCHAR(25),
    business_area VARCHAR(25),
    business_city VARCHAR(25),
    business_country VARCHAR(25),
    business_name VARCHAR(100),
    fssai_no VARCHAR(20),
    gst_no VARCHAR(20),
    owner_name VARCHAR(50),
    support_team_name VARCHAR(50),
    support_team_phone VARCHAR(50),
    whatsapp_no VARCHAR(20),
    rating DOUBLE PRECISION,
    user_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT now(),
    modified_on TIMESTAMP,
    PRIMARY KEY (client_id)
);

-- Add an index on phone_no
CREATE INDEX idx_phone_no ON client_master_table (phone_no);


-- Table: client_info_table
CREATE TABLE client_info_table (
    id           SERIAL PRIMARY KEY,
    client_id    VARCHAR(50),
    about_us     TEXT,
    google       VARCHAR(50),
    insta        VARCHAR(50),
    created_at   TIMESTAMP DEFAULT now(),
    full_address VARCHAR(255),
    lat          DOUBLE PRECISION,
    lang         DOUBLE PRECISION,
    tagline      VARCHAR(255),
    zip_code     VARCHAR(10),
    tags         TEXT[],
    UNIQUE (client_id),
    CONSTRAINT client_info_table_client_id_fkey
        FOREIGN KEY (client_id)
        REFERENCES client_master_table (client_id)
        ON DELETE CASCADE
);

-- Table: client_business_timings
CREATE TABLE client_business_timings (
    timing_id   SERIAL PRIMARY KEY,
    client_id   VARCHAR(50),
    day         VARCHAR(15),
    start_time  TIME,
    end_time    TIME,
    next_day    BOOLEAN,
    active      BOOLEAN,
    CONSTRAINT client_business_timings_client_id_fkey
        FOREIGN KEY (client_id)
        REFERENCES client_master_table (client_id)
        ON DELETE CASCADE
);
