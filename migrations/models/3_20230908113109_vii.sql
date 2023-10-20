-- upgrade --
CREATE TABLE IF NOT EXISTS "eventminute" (
    "is_active" BOOL NOT NULL  DEFAULT True,
    "created" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "content" TEXT,
    "index" INT NOT NULL  DEFAULT 1,
    "author_id" INT REFERENCES "user" ("id") ON DELETE SET NULL,
    "event_id" INT NOT NULL REFERENCES "event" ("id") ON DELETE CASCADE
);
-- downgrade --
DROP TABLE IF EXISTS "eventminute";
