-- upgrade --
ALTER TABLE "eventdocument" ALTER COLUMN "file" TYPE TEXT USING "file"::TEXT;
-- downgrade --
ALTER TABLE "eventdocument" ALTER COLUMN "file" TYPE VARCHAR(100) USING "file"::VARCHAR(100);
