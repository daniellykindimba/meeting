-- upgrade --
CREATE TABLE IF NOT EXISTS "userotp" (
    "is_active" BOOL NOT NULL  DEFAULT True,
    "created" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "token" VARCHAR(100) NOT NULL,
    "phone" VARCHAR(100) NOT NULL,
    "is_used" BOOL NOT NULL  DEFAULT False,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
-- downgrade --
DROP TABLE IF EXISTS "userotp";
