-- upgrade --
CREATE TABLE IF NOT EXISTS "usercommittee" (
    "is_active" BOOL NOT NULL  DEFAULT True,
    "created" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "commitee_id" INT NOT NULL REFERENCES "committee" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
-- downgrade --
DROP TABLE IF EXISTS "usercommittee";
