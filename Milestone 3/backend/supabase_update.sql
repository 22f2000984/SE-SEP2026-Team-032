-- Run this once in the Supabase SQL editor (only if your Supabase database was created BEFORE Sprint 2).
-- New tables (feedback, concern, checkin, email_log) are created by the app itself; only new COLUMNS need SQL.
ALTER TABLE student_profile ADD COLUMN IF NOT EXISTS looking_for_mentor BOOLEAN NOT NULL DEFAULT TRUE;
