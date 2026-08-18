-- auto-generated definition
create table testhub_sessions
(
    created_at            timestamptz  not null,
    updated_at            timestamptz  not null,
    deleted_at            timestamptz  null,
    id                    uuid         not null
        primary key,
    name                  varchar(255) not null,
    status                varchar(16)  not null,
    feature_source_module varchar(64)  not null,
    feature_sha           varchar(64)  not null,
    environment_id        varchar(255) not null,
    selection             jsonb        not null,
    summary               jsonb        not null,
    created_by_id         uuid         null,
    updated_by_id         uuid         null,
    job_id                uuid         null,
    project_id            uuid         not null,
    requested_by_id       uuid         null,
    workspace_id          uuid         not null
);

CREATE INDEX testhub_sess_proj_created_idx ON testhub_sessions USING btree (project_id, created_at DESC);

CREATE INDEX testhub_sessions_created_by_id_2d6874da ON testhub_sessions USING btree (created_by_id);

CREATE INDEX testhub_sessions_job_id_bb981688 ON testhub_sessions USING btree (job_id);

CREATE INDEX testhub_sessions_project_id_2df67299 ON testhub_sessions USING btree (project_id);

CREATE INDEX testhub_sessions_requested_by_id_d61a1321 ON testhub_sessions USING btree (requested_by_id);

CREATE INDEX testhub_sessions_updated_by_id_8156f3ce ON testhub_sessions USING btree (updated_by_id);

CREATE INDEX testhub_sessions_workspace_id_205188a3 ON testhub_sessions USING btree (workspace_id);

