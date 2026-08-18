-- auto-generated definition
create table testhub_jobs
(
    created_at      timestamptz not null,
    updated_at      timestamptz not null,
    deleted_at      timestamptz null,
    id              uuid        not null
        primary key,
    created_by_id   uuid        null,
    updated_by_id   uuid        null,
    kind            varchar(64) not null,
    status          varchar(16) not null,
    params          jsonb       not null,
    argv            jsonb       not null,
    confirmed       boolean     not null,
    exit_code       integer     null,
    stdout          text        not null,
    stderr          text        not null,
    started_at      timestamptz null,
    finished_at     timestamptz null,
    project_id      uuid        not null,
    workspace_id    uuid        not null,
    requested_by_id uuid        null
);

CREATE INDEX testhub_job_proj_created_idx ON testhub_jobs USING btree (project_id, created_at DESC);

CREATE INDEX testhub_job_proj_stat_idx ON testhub_jobs USING btree (project_id, status);

CREATE INDEX testhub_jobs_created_by_id_f2942e86 ON testhub_jobs USING btree (created_by_id);

CREATE INDEX testhub_jobs_project_id_2045fc13 ON testhub_jobs USING btree (project_id);

CREATE INDEX testhub_jobs_requested_by_id_3771cb7d ON testhub_jobs USING btree (requested_by_id);

CREATE INDEX testhub_jobs_updated_by_id_5900b9da ON testhub_jobs USING btree (updated_by_id);

CREATE INDEX testhub_jobs_workspace_id_663c24bb ON testhub_jobs USING btree (workspace_id);

