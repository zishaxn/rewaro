-- Table: customer_master_table
CREATE TABLE customer_master_table (
    customer_id VARCHAR(25) NOT NULL,
    phone_no    VARCHAR(20),
    dob         DATE,
    email_id    VARCHAR(255),
    gender      CHAR(1),
    name        VARCHAR(100),
    user_id     VARCHAR(50),
    created_at  TIMESTAMP DEFAULT now(),
    PRIMARY KEY (customer_id),
    UNIQUE (phone_no, customer_id)
);

-- Create index on phone_no
CREATE INDEX idx_phone_no ON customer_master_table (phone_no);
