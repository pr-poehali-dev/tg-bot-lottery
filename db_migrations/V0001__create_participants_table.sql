CREATE TABLE IF NOT EXISTS participants (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255),
    prize_amount INTEGER NOT NULL,
    prize_label VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_participants_created_at ON participants(created_at DESC);