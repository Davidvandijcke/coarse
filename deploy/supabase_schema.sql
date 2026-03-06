-- Supabase schema for coarse web version
-- Run this in the Supabase SQL editor to set up the database.

-- ============================================================================
-- Profiles (extends Supabase Auth users)
-- ============================================================================

create table profiles (
  id uuid references auth.users on delete cascade primary key,
  tier text not null default 'free' check (tier in ('free', 'byok')),
  openrouter_key text,                     -- API key, BYOK only (plaintext; use Supabase Vault for encryption)
  data_sharing_consent boolean default false,
  consent_date timestamptz,
  created_at timestamptz default now()
);

-- Auto-create profile on signup
create or replace function handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id) values (new.id);
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function handle_new_user();

-- RLS: users can read/update their own profile
alter table profiles enable row level security;

create policy "Users can view own profile"
  on profiles for select using (auth.uid() = id);

create policy "Users can update own profile"
  on profiles for update using (auth.uid() = id);

-- ============================================================================
-- Reviews
-- ============================================================================

create table reviews (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references profiles(id) on delete cascade not null,
  status text not null default 'queued'
    check (status in ('queued', 'running', 'done', 'failed')),
  tier text not null default 'free' check (tier in ('free', 'byok')),
  paper_title text,
  domain text,
  taxonomy text,
  pdf_storage_path text,                   -- path in Supabase Storage
  result_markdown text,                    -- the full review output
  result_json jsonb,                       -- structured Review object
  cost_usd numeric(8,4),                   -- actual LLM cost
  duration_seconds int,
  error_message text,
  shareable boolean default false,         -- user opted to share publicly
  data_shared_for_research boolean default false,
  created_at timestamptz default now(),
  completed_at timestamptz
);

-- Index for rate limiting queries
create index idx_reviews_user_created on reviews(user_id, created_at);

-- Index for public sharing
create index idx_reviews_shareable on reviews(id) where shareable = true;

-- RLS: users see their own reviews + publicly shared reviews
alter table reviews enable row level security;

create policy "Users can view own reviews"
  on reviews for select using (auth.uid() = user_id);

create policy "Anyone can view shared reviews"
  on reviews for select using (shareable = true);

create policy "Users can insert own reviews"
  on reviews for insert with check (auth.uid() = user_id);

create policy "Users can update own reviews"
  on reviews for update using (auth.uid() = user_id);

-- ============================================================================
-- Storage buckets
-- ============================================================================

insert into storage.buckets (id, name, public) values ('papers', 'papers', false);
insert into storage.buckets (id, name, public) values ('results', 'results', true);

-- Papers bucket: users can upload/read only their own files (path prefix = user_id/)
create policy "Users upload own papers"
  on storage.objects for insert
  with check (bucket_id = 'papers' and (storage.foldername(name))[1] = auth.uid()::text);

create policy "Users read own papers"
  on storage.objects for select
  using (bucket_id = 'papers' and (storage.foldername(name))[1] = auth.uid()::text);

-- Results bucket: public read (for shared reviews)
create policy "Public read results"
  on storage.objects for select
  using (bucket_id = 'results');

-- ============================================================================
-- Helper: rate limiting function
-- ============================================================================

create or replace function check_rate_limit(p_user_id uuid)
returns boolean as $$
declare
  today_count int;
  month_count int;
  user_tier text;
begin
  select tier into user_tier from profiles where id = p_user_id;

  -- BYOK users have no rate limit
  if user_tier = 'byok' then
    return true;
  end if;

  -- Free tier: 5/day, 30/month (exclude failed reviews)
  select count(*) into today_count
  from reviews
  where user_id = p_user_id
    and created_at >= current_date
    and status != 'failed';

  if today_count >= 5 then
    return false;
  end if;

  select count(*) into month_count
  from reviews
  where user_id = p_user_id
    and created_at >= date_trunc('month', current_date)
    and status != 'failed';

  if month_count >= 30 then
    return false;
  end if;

  return true;
end;
$$ language plpgsql security definer;

-- ============================================================================
-- Realtime: enable for review status updates
-- ============================================================================

alter publication supabase_realtime add table reviews;
