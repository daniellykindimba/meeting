-- upgrade --
ALTER TABLE "eventagenda" DROP COLUMN "index";
-- downgrade --
ALTER TABLE "eventagenda" ADD "index" INT NOT NULL  DEFAULT 1;
