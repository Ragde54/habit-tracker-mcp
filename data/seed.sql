-- categories shared by both habits and todos
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,       -- 'health', 'learning', 'work'
    color TEXT                        -- '#FF5733' for UI hints
);

-- the habit definition
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER REFERENCES categories(id),
    name TEXT NOT NULL,
    description TEXT,
    frequency_type TEXT NOT NULL CHECK (frequency_type IN ('daily', 'weekly', 'monthly')),
    frequency_target INTEGER NOT NULL DEFAULT 1,  -- X times per period
    created_at TEXT DEFAULT (datetime('now')),
    archived_at TEXT                              -- soft delete
);

-- each time a habit is completed
CREATE TABLE IF NOT EXISTS habit_completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL REFERENCES habits(id),
    completed_at TEXT DEFAULT (datetime('now')),
    note TEXT                                     -- optional journal entry
);

-- standalone todos
CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER REFERENCES categories(id),
    habit_id INTEGER REFERENCES habits(id),       -- nullable: links to a habit if relevant
    title TEXT NOT NULL,
    notes TEXT,
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    due_date TEXT,
    completed_at TEXT,                            -- NULL means not done yet
    created_at TEXT DEFAULT (datetime('now'))
);