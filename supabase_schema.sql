-- ShaileshGPT Supabase Analytics Schema
-- Run this once inside Supabase:
-- Supabase Dashboard -> SQL Editor -> New Query -> paste this file -> Run

create table if not exists public.visitors (
  visitor_id text primary key,
  name text not null,
  email text not null unique,
  phone text,
  linkedin text,
  github text,
  website text,
  other_contact text,
  source text,
  user_agent text,
  ip_address text,
  created_at timestamptz not null default now(),
  last_seen_at timestamptz not null default now()
);

create table if not exists public.interactions (
  interaction_id text primary key,
  visitor_id text not null references public.visitors(visitor_id) on delete cascade,
  visitor_name text,
  visitor_email text,
  channel text not null,
  interaction_type text not null,
  question text not null,
  answer_preview text,
  metadata_json jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_visitors_email on public.visitors(email);
create index if not exists idx_visitors_last_seen on public.visitors(last_seen_at desc);
create index if not exists idx_interactions_visitor on public.interactions(visitor_id);
create index if not exists idx_interactions_created on public.interactions(created_at desc);

-- Recommended: keep Row Level Security enabled for dashboard safety.
-- The backend uses the service-role key, which can access these tables securely server-side.
alter table public.visitors enable row level security;
alter table public.interactions enable row level security;
