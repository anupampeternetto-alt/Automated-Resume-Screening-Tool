PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY NOT NULL,
    title TEXT NOT NULL,
    jd_text TEXT NOT NULL,
    must_have TEXT NOT NULL DEFAULT '[]'
        CHECK (json_valid(must_have)),
    nice_to_have TEXT NOT NULL DEFAULT '[]'
        CHECK (json_valid(nice_to_have)),
    min_exp_years REAL NOT NULL DEFAULT 0
        CHECK (min_exp_years >= 0),
    location TEXT
);

CREATE TABLE IF NOT EXISTS candidates (
    id TEXT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    location TEXT
);

CREATE TABLE IF NOT EXISTS resumes (
    candidate_id TEXT PRIMARY KEY NOT NULL,
    source TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    parsed_json TEXT NOT NULL DEFAULT '{}'
        CHECK (json_valid(parsed_json)),
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id)
        REFERENCES candidates(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS features (
    candidate_id TEXT NOT NULL,
    job_id TEXT NOT NULL,
    sim_embedding REAL NOT NULL
        CHECK (sim_embedding BETWEEN -1 AND 1),
    rule_musthave_hits INTEGER NOT NULL
        CHECK (rule_musthave_hits >= 0),
    rule_musthave_total INTEGER NOT NULL
        CHECK (rule_musthave_total >= 0),
    years_exp REAL NOT NULL DEFAULT 0
        CHECK (years_exp >= 0),
    gap_penalty REAL NOT NULL DEFAULT 0
        CHECK (gap_penalty >= 0),
    CHECK (rule_musthave_hits <= rule_musthave_total),
    PRIMARY KEY (candidate_id, job_id),
    FOREIGN KEY (candidate_id)
        REFERENCES candidates(id)
        ON DELETE CASCADE,
    FOREIGN KEY (job_id)
        REFERENCES jobs(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rankings (
    job_id TEXT NOT NULL,
    candidate_id TEXT NOT NULL,
    score REAL NOT NULL,
    reasons TEXT NOT NULL
        CHECK (json_valid(reasons)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (job_id, candidate_id),
    FOREIGN KEY (job_id)
        REFERENCES jobs(id)
        ON DELETE CASCADE,
    FOREIGN KEY (candidate_id)
        REFERENCES candidates(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_rankings_job_score
ON rankings(job_id, score DESC);

CREATE INDEX IF NOT EXISTS idx_features_job
ON features(job_id);