import psycopg2

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="propdb",
    user="propuser",
    password="proppass123",
    host="localhost",
    port="5432"
)
c = conn.cursor()

# USERS TABLE
c.execute("DROP TABLE IF EXISTS users CASCADE;")
c.execute("""
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    team TEXT,
    phone TEXT,
    ren_no TEXT,
    nric TEXT,
    tiering_pct NUMERIC(5,2),
    position TEXT,
    notes TEXT,
    expiry_year INTEGER,
    registration_fee_paid BOOLEAN DEFAULT FALSE,
    kit_bag BOOLEAN DEFAULT FALSE,
    kit_black_file BOOLEAN DEFAULT FALSE,
    kit_lanyard BOOLEAN DEFAULT FALSE,
    kit_tg_id BOOLEAN DEFAULT FALSE,
    kit_biz_card BOOLEAN DEFAULT FALSE,
    kit_tshirt BOOLEAN DEFAULT FALSE,
    kit_remarks TEXT,
    bank_name TEXT,
    bank_account TEXT,
    status TEXT DEFAULT 'active',
    added_by INTEGER,
    reset_token TEXT,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# CASES TABLE
c.execute("DROP TABLE IF EXISTS cases CASCADE;")
c.execute("""
CREATE TABLE cases (
    case_id SERIAL PRIMARY KEY,
    number INTEGER,
    case_no TEXT,
    invoice_no TEXT,
    eform_id TEXT,
    agent_id INTEGER REFERENCES users(user_id),
    leader_id INTEGER REFERENCES users(user_id),
    agent_name TEXT,
    leader_name TEXT,
    client_name TEXT,
    property_address TEXT,
    description TEXT,
    case_details TEXT,
    purchase_price NUMERIC(12,2),
    amount NUMERIC(12,2),
    fee_pct NUMERIC(7,2),
    commission_pct NUMERIC(7,2),
    commission_total NUMERIC(12,2),
    override_leader_amt NUMERIC(12,2),
    override_hoa_amt NUMERIC(12,2),
    profit_proper NUMERIC(12,2),
    ed_paid NUMERIC(12,2),
    ed_pending TEXT,
    tax NUMERIC(12,2),
    total_amount NUMERIC(12,2),
    reference_no TEXT,
    registration_no TEXT,
    mode_of_payment TEXT,
    in_part_payment_of TEXT,
    date_created TEXT,
    payment_status TEXT,
    case_status TEXT
);
""")

# INVOICES TABLE
c.execute("DROP TABLE IF EXISTS invoices CASCADE;")
c.execute("""
CREATE TABLE invoices (
    invoice_id SERIAL PRIMARY KEY,
    invoice_no TEXT UNIQUE,
    case_id INTEGER REFERENCES cases(case_id),
    agent_id INTEGER REFERENCES users(user_id),
    leader_id INTEGER REFERENCES users(user_id),
    agent_commission NUMERIC(12,2),
    leader_commission NUMERIC(12,2),
    admin_commission NUMERIC(12,2),
    commission_pct NUMERIC(5,2),
    commission_total NUMERIC(12,2),
    tax NUMERIC(12,2),
    total_amount NUMERIC(12,2),
    date_issued TEXT,
    property_address TEXT,
    remarks TEXT
);
""")

# LEDGER TABLE
c.execute("DROP TABLE IF EXISTS ledger CASCADE;")
c.execute("""
CREATE TABLE ledger (
    ledger_id SERIAL PRIMARY KEY,
    invoice_id INTEGER REFERENCES invoices(invoice_id),
    amount_paid NUMERIC(12,2),
    date_paid TEXT,
    payment_method TEXT,
    payment_note TEXT,
    file_reference_no TEXT,
    in_part_payment_of TEXT
);
""")

# REGISTRATION REQUESTS TABLE
c.execute("DROP TABLE IF EXISTS registration_requests CASCADE;")
c.execute("""
CREATE TABLE registration_requests (
    request_id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    phone TEXT,
    team TEXT,
    role TEXT,
    password_hash TEXT,
    nric TEXT,
    dob DATE,
    status TEXT DEFAULT 'pending',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# COMMISSION RECORDS TABLE
c.execute("DROP TABLE IF EXISTS commission_records CASCADE;")
c.execute("""
CREATE TABLE commission_records (
    record_id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES cases(case_id),
    agent_id INTEGER REFERENCES users(user_id),
    team TEXT,
    account_no TEXT,
    commission_total NUMERIC(12,2),
    fifty_pct NUMERIC(12,2),
    coa_deduction NUMERIC(12,2),
    commission_agent_rm NUMERIC(12,2),
    agent_pct NUMERIC(5,2),
    team_leader_pct NUMERIC(5,2),
    team_leader_rm NUMERIC(12,2),
    hoa_pct NUMERIC(5,2),
    hoa_rm NUMERIC(12,2),
    proper_pct TEXT,
    proper_rm NUMERIC(12,2),
    claim_date DATE,
    payment_status TEXT DEFAULT 'Pending',
    payment_date DATE
);
""")

# ED CLOSURES TABLE
c.execute("DROP TABLE IF EXISTS ed_closures CASCADE;")
c.execute("""
CREATE TABLE ed_closures (
    closure_id SERIAL PRIMARY KEY,
    agent_id INTEGER REFERENCES users(user_id),
    team TEXT,
    ren_no TEXT,
    case_no TEXT,
    purchase_price NUMERIC(12,2),
    total_ed NUMERIC(12,2),        -- 3.24% of purchase price
    ed_converted NUMERIC(12,2),    -- Converted to commission
    commission_agent NUMERIC(12,2),
    remarks TEXT
);
""")

# ED SUMMARY TABLE
c.execute("DROP TABLE IF EXISTS ed_summary CASCADE;")
c.execute("""
CREATE TABLE ed_summary (
    summary_id SERIAL PRIMARY KEY,
    agent_id INTEGER REFERENCES users(user_id),
    team TEXT,
    ren_no TEXT,
    total_closer NUMERIC(12,2),         -- Total ED expected
    total_ed_claimed NUMERIC(12,2),     -- Total converted
    quarter TEXT,                       -- e.g., 'Q1 2025'
    is_top_closer BOOLEAN DEFAULT FALSE,
    is_top_active_player BOOLEAN DEFAULT FALSE
);
""")

# COMPANY SETTINGS TABLE
c.execute("DROP TABLE IF EXISTS company_settings CASCADE;")
c.execute("""
CREATE TABLE company_settings (
    setting_id SERIAL PRIMARY KEY,
    company_name TEXT,
    firm_reg_no TEXT,
    address TEXT,
    phone TEXT,
    email TEXT,
    bank_name TEXT,
    bank_account TEXT
);
""")

# Insert Default Company Setting
c.execute("""
INSERT INTO company_settings (
    company_name, firm_reg_no, address, phone, email, bank_name, bank_account
) VALUES (
    'Property Excel Realty',
    '202203276720 (KT0533995-X)',
    'B-7-18, OASIS SQUARE, JALAN PJU 1A/7, OASIS ARA DAMANSARA, 47301 PETALING JAYA, SELANGOR',
    '012-755 7099',
    'propertyexcelrealty@gmail.com',
    'MAYBANK',
    '512312312321'
);
""")

# Final Commit
conn.commit()
conn.close()
print("✅ PostgreSQL cleared and Initiated.")