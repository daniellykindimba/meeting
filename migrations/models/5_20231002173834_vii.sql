-- upgrade --
ALTER TABLE "eventattendee" ADD "manage_agendas" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "eventattendee" ADD "manage_minutes" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "eventattendee" ADD "can_upload" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "eventattendee" DROP COLUMN "manage_agendas";
ALTER TABLE "eventattendee" DROP COLUMN "manage_minutes";
ALTER TABLE "eventattendee" DROP COLUMN "can_upload";
