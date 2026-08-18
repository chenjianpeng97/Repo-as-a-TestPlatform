-- auto-generated definition
create table github_repository_syncs
(
    created_at               timestamptz not null,
    updated_at               timestamptz not null,
    id                       uuid        not null
        primary key,
    credentials              jsonb       not null,
    actor_id                 uuid        not null,
    created_by_id            uuid        null,
    label_id                 uuid        null,
    project_id               uuid        not null,
    repository_id            uuid        not null,
    updated_by_id            uuid        null,
    workspace_id             uuid        not null,
    workspace_integration_id uuid        not null,
    deleted_at               timestamptz null
);

CREATE INDEX github_repository_syncs_actor_id_1fa689fe ON github_repository_syncs USING btree (actor_id);

CREATE INDEX github_repository_syncs_created_by_id_0df94495 ON github_repository_syncs USING btree (created_by_id);

CREATE INDEX github_repository_syncs_label_id_eb1e9bd7 ON github_repository_syncs USING btree (label_id);

CREATE INDEX github_repository_syncs_project_id_e7e8291e ON github_repository_syncs USING btree (project_id);

CREATE INDEX github_repository_syncs_updated_by_id_07e9d065 ON github_repository_syncs USING btree (updated_by_id);

CREATE INDEX github_repository_syncs_workspace_id_4a22a8b8 ON github_repository_syncs USING btree (workspace_id);

CREATE INDEX github_repository_syncs_workspace_integration_id_62858398 ON github_repository_syncs USING btree (workspace_integration_id);

CREATE UNIQUE INDEX github_repository_syncs_project_id_repository_id_0f3705e6_uniq ON github_repository_syncs USING btree (project_id, repository_id);

CREATE UNIQUE INDEX github_repository_syncs_repository_id_key ON github_repository_syncs USING btree (repository_id);

