-- upgrade --
ALTER TABLE "eventagenda" ADD "index" INT NOT NULL  DEFAULT 1;
-- downgrade --
ALTER TABLE "eventagenda" DROP COLUMN "index";
