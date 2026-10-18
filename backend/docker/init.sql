-- Docker init SQL
-- Database initialization script

-- Create extensions
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create database if not exists (handled by POSTGRES_DB env var)
-- This file runs on first container start

-- Additional configurations
SET statement_timeout = '300s';