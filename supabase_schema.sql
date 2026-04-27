-- ShaileshGPT Supabase Admin + Analytics + Conversation History Schema
-- Run in Supabase Dashboard -> SQL Editor -> New Query -> Run

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

create table if not exists public.conversation_sessions (
  session_id text primary key,
  visitor_id text not null references public.visitors(visitor_id) on delete cascade,
  visitor_name text,
  visitor_email text,
  source text,
  created_at timestamptz not null default now(),
  last_activity_at timestamptz not null default now()
);

create table if not exists public.interactions (
  interaction_id text primary key,
  visitor_id text not null references public.visitors(visitor_id) on delete cascade,
  visitor_name text,
  visitor_email text,
  session_id text references public.conversation_sessions(session_id) on delete set null,
  channel text not null,
  interaction_type text not null,
  question text not null,
  normalized_question text,
  answer_preview text,
  metadata_json jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.conversation_messages (
  message_id text primary key,
  session_id text not null references public.conversation_sessions(session_id) on delete cascade,
  visitor_id text not null references public.visitors(visitor_id) on delete cascade,
  interaction_id text references public.interactions(interaction_id) on delete set null,
  role text not null check (role in ('user', 'assistant', 'system')),
  content text not null,
  created_at timestamptz not null default now()
);

create index if not exists idx_visitors_email on public.visitors(email);
create index if not exists idx_visitors_last_seen on public.visitors(last_seen_at desc);
create index if not exists idx_sessions_visitor on public.conversation_sessions(visitor_id);
create index if not exists idx_sessions_last_activity on public.conversation_sessions(last_activity_at desc);
create index if not exists idx_interactions_visitor on public.interactions(visitor_id);
create index if not exists idx_interactions_session on public.interactions(session_id);
create index if not exists idx_interactions_created on public.interactions(created_at desc);
create index if not exists idx_interactions_normalized_question on public.interactions(normalized_question);
create index if not exists idx_messages_session on public.conversation_messages(session_id);
create index if not exists idx_messages_visitor on public.conversation_messages(visitor_id);
create index if not exists idx_messages_created on public.conversation_messages(created_at desc);

alter table public.visitors enable row level security;
alter table public.conversation_sessions enable row level security;
alter table public.interactions enable row level security;
alter table public.conversation_messages enable row level security;
