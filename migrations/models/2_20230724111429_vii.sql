-- upgrade --
CREATE TABLE IF NOT EXISTS "committee" (
    "is_active" BOOL NOT NULL  DEFAULT True,
    "created" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "description" TEXT
);;
ALTER TABLE "eventdocument" ADD "author_id" INT;
CREATE TABLE IF NOT EXISTS "usercommittee" (
    "is_active" BOOL NOT NULL  DEFAULT True,
    "created" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "committee_id" INT NOT NULL REFERENCES "committee" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);;
ALTER TABLE "eventdocument" ADD CONSTRAINT "fk_eventdoc_user_ad699a84" FOREIGN KEY ("author_id") REFERENCES "user" ("id") ON DELETE SET NULL;
-- downgrade --
ALTER TABLE "eventdocument" DROP CONSTRAINT "fk_eventdoc_user_ad699a84";
ALTER TABLE "eventdocument" DROP COLUMN "author_id";
DROP TABLE IF EXISTS "committee";
DROP TABLE IF EXISTS "usercommittee";
