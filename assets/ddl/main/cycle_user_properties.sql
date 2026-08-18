-- auto-generated definition
create table cycle_user_properties
(
    created_at         timestamptz not null,
    updated_at         timestamptz not null,
    id                 uuid        not null
        primary key,
    filters            jsonb       not null,
    display_filters    jsonb       not null,
    display_properties jsonb       not null,
    created_by_id      uuid        null,
    cycle_id           uuid        not null,
    project_id         uuid        not null,
    updated_by_id      uuid        null,
    user_id            uuid        not null,
    workspace_id       uuid        not null,
    deleted_at         timestamptz null,
    rich_filters       jsonb       not null
);

CREATE INDEX cycle_user_properties_created_by_id_501f371c ON cycle_user_properties USING btree (created_by_id);

CREATE INDEX cycle_user_properties_cycle_id_1f8bdf35 ON cycle_user_properties USING btree (cycle_id);

CREATE INDEX cycle_user_properties_project_id_4efc0f07 ON cycle_user_properties USING btree (project_id);

CREATE INDEX cycle_user_properties_updated_by_id_1b5ac27b ON cycle_user_properties USING btree (updated_by_id);

CREATE INDEX cycle_user_properties_user_id_9e9ef97d ON cycle_user_properties USING btree (user_id);

CREATE INDEX cycle_user_properties_workspace_id_62d65d71 ON cycle_user_properties USING btree (workspace_id);

CREATE UNIQUE INDEX cycle_user_properties_cycle_id_user_id_deleted_at_fbe00cf4_uniq ON cycle_user_properties USING btree (cycle_id, user_id, deleted_at);

CREATE UNIQUE INDEX cycle_user_properties_unique_cycle_user_when_deleted_at_null ON cycle_user_properties USING btree (cycle_id, user_id) WHERE (deleted_at IS NULL);

