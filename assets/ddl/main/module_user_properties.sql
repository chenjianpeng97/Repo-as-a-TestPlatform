-- auto-generated definition
create table module_user_properties
(
    created_at         timestamptz not null,
    updated_at         timestamptz not null,
    id                 uuid        not null
        primary key,
    filters            jsonb       not null,
    display_filters    jsonb       not null,
    display_properties jsonb       not null,
    created_by_id      uuid        null,
    module_id          uuid        not null,
    project_id         uuid        not null,
    updated_by_id      uuid        null,
    user_id            uuid        not null,
    workspace_id       uuid        not null,
    deleted_at         timestamptz null,
    rich_filters       jsonb       not null
);

CREATE INDEX module_user_properties_created_by_id_bdd98440 ON module_user_properties USING btree (created_by_id);

CREATE INDEX module_user_properties_module_id_e95b158a ON module_user_properties USING btree (module_id);

CREATE INDEX module_user_properties_project_id_3c5a4972 ON module_user_properties USING btree (project_id);

CREATE INDEX module_user_properties_updated_by_id_b7dafc77 ON module_user_properties USING btree (updated_by_id);

CREATE INDEX module_user_properties_user_id_e83a1c2c ON module_user_properties USING btree (user_id);

CREATE INDEX module_user_properties_workspace_id_ddaf807c ON module_user_properties USING btree (workspace_id);

CREATE UNIQUE INDEX module_user_properties_module_id_user_id_delete_3269582d_uniq ON module_user_properties USING btree (module_id, user_id, deleted_at);

CREATE UNIQUE INDEX module_user_properties_unique_module_user_when_deleted_at_null ON module_user_properties USING btree (module_id, user_id) WHERE (deleted_at IS NULL);

