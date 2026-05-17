-- Weekly check-in progress for mission plans

alter table mission_plans
  add column if not exists week_progress jsonb not null default '{}'::jsonb;
