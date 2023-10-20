-- upgrade --
ALTER TABLE "event" ADD "financial_year" VARCHAR(100);
-- downgrade --
ALTER TABLE "event" DROP COLUMN "financial_year";
