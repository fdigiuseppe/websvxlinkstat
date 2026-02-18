-- Schema database SQLite per SVXLink Log Analyzer
-- Gestisce statistiche giornaliere, mensili e annuali

-- Tabella principale per i log giornalieri
CREATE TABLE IF NOT EXISTS daily_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    file_size INTEGER,
    total_transmissions INTEGER DEFAULT 0,
    total_transmission_time INTEGER DEFAULT 0, -- secondi
    avg_transmission_time REAL DEFAULT 0,
    max_transmission_time INTEGER DEFAULT 0,
    min_transmission_time INTEGER DEFAULT 0,
    total_qso INTEGER DEFAULT 0,
    total_qso_time INTEGER DEFAULT 0,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella per statistiche CTCSS giornaliere
CREATE TABLE IF NOT EXISTS daily_ctcss_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date DATE NOT NULL,
    ctcss_frequency REAL NOT NULL,
    count INTEGER NOT NULL,
    percentage REAL NOT NULL,
    FOREIGN KEY (log_date) REFERENCES daily_logs(date),
    UNIQUE(log_date, ctcss_frequency)
);

-- Tabella per statistiche Talk Group giornaliere
CREATE TABLE IF NOT EXISTS daily_tg_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date DATE NOT NULL,
    tg_number INTEGER NOT NULL,
    transmission_count INTEGER NOT NULL,
    total_duration INTEGER NOT NULL, -- secondi
    qso_count INTEGER NOT NULL,
    avg_duration REAL NOT NULL,
    percentage REAL NOT NULL,
    FOREIGN KEY (log_date) REFERENCES daily_logs(date),
    UNIQUE(log_date, tg_number)
);

-- Tabella per eventi QSO dettagliati
CREATE TABLE IF NOT EXISTS daily_qso_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date DATE NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    duration INTEGER NOT NULL, -- secondi
    tg_number INTEGER,
    ctcss_frequency REAL,
    event_type TEXT, -- 'qso', 'transmission', 'other'
    details TEXT, -- JSON con dettagli aggiuntivi
    FOREIGN KEY (log_date) REFERENCES daily_logs(date)
);

-- Tabella per statistiche mensili aggregate
CREATE TABLE IF NOT EXISTS monthly_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    total_days INTEGER NOT NULL,
    total_transmissions INTEGER DEFAULT 0,
    total_transmission_time INTEGER DEFAULT 0,
    avg_daily_transmissions REAL DEFAULT 0,
    avg_daily_time REAL DEFAULT 0,
    total_qso INTEGER DEFAULT 0,
    most_active_day DATE,
    most_used_ctcss REAL,
    most_used_tg INTEGER,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, month)
);

-- Tabella per statistiche annuali aggregate
CREATE TABLE IF NOT EXISTS yearly_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL UNIQUE,
    total_days INTEGER NOT NULL,
    total_transmissions INTEGER DEFAULT 0,
    total_transmission_time INTEGER DEFAULT 0,
    avg_monthly_transmissions REAL DEFAULT 0,
    avg_monthly_time REAL DEFAULT 0,
    total_qso INTEGER DEFAULT 0,
    most_active_month INTEGER,
    most_active_day DATE,
    peak_hour INTEGER, -- ora di picco (0-23)
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella per tracciare disconnessioni ReflectorLogic
CREATE TABLE IF NOT EXISTS daily_disconnections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date DATE NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration INTEGER, -- secondi (NULL se disconnessione ancora in corso)
    disconnection_count INTEGER DEFAULT 1, -- numero di disconnessioni nel periodo
    status TEXT DEFAULT 'resolved', -- 'resolved' o 'ongoing'
    FOREIGN KEY (log_date) REFERENCES daily_logs(date)
);

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_daily_logs_date ON daily_logs(date);
CREATE INDEX IF NOT EXISTS idx_ctcss_stats_date ON daily_ctcss_stats(log_date);
CREATE INDEX IF NOT EXISTS idx_tg_stats_date ON daily_tg_stats(log_date);
CREATE INDEX IF NOT EXISTS idx_qso_events_date ON daily_qso_events(log_date);
CREATE INDEX IF NOT EXISTS idx_qso_events_time ON daily_qso_events(start_time, end_time);
CREATE INDEX IF NOT EXISTS idx_monthly_stats_period ON monthly_stats(year, month);
CREATE INDEX IF NOT EXISTS idx_disconnections_date ON daily_disconnections(log_date);
CREATE INDEX IF NOT EXISTS idx_yearly_stats_year ON yearly_stats(year);

-- Views per query comuni
CREATE VIEW IF NOT EXISTS v_daily_summary AS
SELECT 
    dl.date,
    dl.total_transmissions,
    dl.total_transmission_time,
    dl.total_qso,
    COUNT(DISTINCT dcs.ctcss_frequency) as unique_ctcss,
    COUNT(DISTINCT dts.tg_number) as unique_tgs,
    GROUP_CONCAT(DISTINCT dcs.ctcss_frequency ORDER BY dcs.count DESC) as top_ctcss,
    GROUP_CONCAT(DISTINCT dts.tg_number ORDER BY dts.transmission_count DESC) as top_tgs
FROM daily_logs dl
LEFT JOIN daily_ctcss_stats dcs ON dl.date = dcs.log_date
LEFT JOIN daily_tg_stats dts ON dl.date = dts.log_date
GROUP BY dl.date
ORDER BY dl.date DESC;

CREATE VIEW IF NOT EXISTS v_monthly_summary AS
SELECT 
    strftime('%Y', date) as year,
    strftime('%m', date) as month,
    COUNT(*) as days_count,
    SUM(total_transmissions) as month_transmissions,
    SUM(total_transmission_time) as month_time,
    SUM(total_qso) as month_qso,
    AVG(total_transmissions) as avg_daily_transmissions,
    MAX(total_transmissions) as peak_daily_transmissions,
    date as peak_day
FROM daily_logs
GROUP BY strftime('%Y-%m', date)
ORDER BY year DESC, month DESC;