-- upgrade --
CREATE TABLE IF NOT EXISTS "eventcommittee" (
    "is_active" BOOL NOT NULL  DEFAULT True,
    "created" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "committee_id" INT NOT NULL REFERENCES "committee" ("id") ON DELETE CASCADE,
    "event_id" INT NOT NULL REFERENCES "event" ("id") ON DELETE CASCADE
);
-- downgrade --
DROP TABLE IF EXISTS "eventcommittee";
