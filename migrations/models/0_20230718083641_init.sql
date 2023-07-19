-- upgrade --
CREATE TABLE IF NOT EXISTS "department" (
    "is_active" BOOL NOT NULL  DEFAULT True,
    "created" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "description" TEXT
);
CREATE TABLE IF NOT EXISTS "user" (
    "is_active" BOOL NOT NULL  DEFAULT True,
    "created" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "first_name" VARCHAR(100) NOT NULL,
    "middle_name" VARCHAR(100),
    "last_name" VARCHAR(100) NOT NULL,
    "email" VARCHAR(100),
    "phone" VARCHAR(100),
    "username" VARCHAR(100) NOT NULL,
    "salt_key" VARCHAR(500),
    "hash_password" VARCHAR(500),
    "is_admin" BOOL NOT NULL  DEFAULT False,
    "is_staff" BOOL NOT NULL  DEFAULT False,
    "avatar" VARCHAR(100)
);
CREATE TABLE IF NOT EXISTS "userdepartment" (
    "is_active" BOOL NOT NULL  DEFAULT True,
    "created" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "department_id" INT NOT NULL REFERENCES "department" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "venue" (
    "is_active" BOOL NOT NULL  DEFAULT True,
    "created" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "description" TEXT,
    "venue_type" VARCHAR(6) NOT NULL  DEFAULT 'room',
    "capacity" INT NOT NULL  DEFAULT 0
);
COMMENT ON COLUMN "venue"."venue_type" IS 'HALL: hall\nROOM: room\nGROUND: ground\nOTHER: other';
CREATE TABLE IF NOT EXISTS "event" (
    "is_active" BOOL NOT NULL  DEFAULT True,
    "created" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(100) NOT NULL,
    "description" TEXT,
    "event_type" VARCHAR(8) NOT NULL  DEFAULT 'meeting',
    "start_time" TIMESTAMPTZ,
    "end_time" TIMESTAMPTZ,
    "author_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "venue_id" INT NOT NULL REFERENCES "venue" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "event"."event_type" IS 'MEETING: meeting\nTRAINING: training\nOTHER: other';
CREATE TABLE IF NOT EXISTS "eventagenda" (
    "is_active" BOOL NOT NULL  DEFAULT True,
    "created" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(100) NOT NULL,
    "description" TEXT,
    "start_time" TIMESTAMPTZ,
    "end_time" TIMESTAMPTZ,
    "event_id" INT NOT NULL REFERENCES "event" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "eventattendee" (
    "is_active" BOOL NOT NULL  DEFAULT True,
    "created" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "is_attending" BOOL NOT NULL  DEFAULT False,
    "attendee_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "event_id" INT NOT NULL REFERENCES "event" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "eventdepartment" (
    "is_active" BOOL NOT NULL  DEFAULT True,
    "created" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "department_id" INT NOT NULL REFERENCES "department" ("id") ON DELETE CASCADE,
    "event_id" INT NOT NULL REFERENCES "event" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "eventdocument" (
    "is_active" BOOL NOT NULL  DEFAULT True,
    "created" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(100) NOT NULL,
    "description" TEXT,
    "file" VARCHAR(100) NOT NULL,
    "event_id" INT NOT NULL REFERENCES "event" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
