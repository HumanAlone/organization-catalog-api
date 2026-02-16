-- Схема БД

CREATE TABLE building (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address VARCHAR(255) NOT NULL,
    latitude DECIMAL(9,6) NOT NULL CHECK (latitude BETWEEN -90 AND 90),
    longitude DECIMAL(9,6) NOT NULL CHECK (longitude BETWEEN -180 AND 180)
);

CREATE TABLE organization (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    building_id INTEGER NOT NULL REFERENCES building(id) ON DELETE RESTRICT
);

CREATE TABLE phone (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number VARCHAR(25) NOT NULL,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
    UNIQUE(number, organization_id)
);

CREATE TABLE business (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    parent_id INTEGER REFERENCES business(id) ON DELETE SET NULL,
    UNIQUE(name, parent_id)
);

CREATE TABLE organization_business (
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
    business_id INTEGER NOT NULL REFERENCES business(id) ON DELETE CASCADE,
    PRIMARY KEY (organization_id, business_id)
);

-- Индексы
CREATE INDEX idx_organization_building ON organization(building_id);
CREATE INDEX idx_phone_number ON phone(number);
CREATE INDEX idx_phone_organization ON phone(organization_id);
CREATE INDEX idx_business_parent ON business(parent_id);
CREATE INDEX idx_org_business_org ON organization_business(organization_id);
CREATE INDEX idx_org_business_business ON organization_business(business_id);
CREATE INDEX idx_building_coords ON building(latitude, longitude);
