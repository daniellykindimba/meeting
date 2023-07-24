-- upgrade --
ALTER TABLE "userotp" ALTER COLUMN "phone" DROP NOT NULL;
-- downgrade --
ALTER TABLE "userotp" ALTER COLUMN "phone" SET NOT NULL;
