-- Career Roadmap — initial schema (run in Supabase SQL editor when ready)

create extension if not exists "pgcrypto";

create table if not exists intake_submissions (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  form_data jsonb not null,
  status text not null default 'submitted'
    check (status in ('submitted', 'processing', 'tracks_ready', 'completed', 'failed'))
);

create table if not exists mission_plans (
  id uuid primary key default gen_random_uuid(),
  intake_id uuid not null references intake_submissions (id) on delete cascade,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  status text not null default 'pending'
    check (status in ('pending', 'picking_tracks', 'awaiting_track_choice', 'generating', 'completed', 'failed')),
  chosen_track_type text check (chosen_track_type in ('Stretch', 'Realistic', 'Safe')),
  agent_outputs jsonb not null default '{}'::jsonb,
  llm_cost_inr numeric(10, 2) not null default 0,
  llm_token_log jsonb not null default '[]'::jsonb
);

create index if not exists idx_mission_plans_intake_id on mission_plans (intake_id);

create or replace function set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger intake_submissions_updated_at
  before update on intake_submissions
  for each row execute function set_updated_at();

create trigger mission_plans_updated_at
  before update on mission_plans
  for each row execute function set_updated_at();
