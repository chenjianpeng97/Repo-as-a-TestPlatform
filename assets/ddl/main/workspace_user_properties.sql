-- auto-generated definition
create table workspace_user_properties
(
    created_at                    timestamptz not null,
    updated_at                    timestamptz not null,
    id                            uuid        not null
        primary key,
    filters                       jsonb       not null,
    display_filters               jsonb       not null,
    display_properties            jsonb       not null,
    created_by_id                 uuid        null,
    updated_by_id                 uuid        null,
    user_id                       uuid        not null,
    workspace_id                  uuid        not null,
    deleted_at                    timestamptz null,
    rich_filters                  jsonb       not null,
    navigation_control_preference varchar(25) not null,
    navigation_project_limit      integer     not null
);

CREATE INDEX workspace_user_properties_created_by_id_6d8d1c4e ON workspace_user_properties USING btree (created_by_id);

CREATE INDEX workspace_user_properties_updated_by_id_910a2cc5 ON workspace_user_properties USING btree (updated_by_id);

CREATE INDEX workspace_user_properties_user_id_b1079e07 ON workspace_user_properties USING btree (user_id);

CREATE INDEX workspace_user_properties_workspace_id_1dc3e2a6 ON workspace_user_properties USING btree (workspace_id);

CREATE UNIQUE INDEX workspace_user_propertie_workspace_id_user_id_del_a7cf15bc_uniq ON workspace_user_properties USING btree (workspace_id, user_id, deleted_at);

CREATE UNIQUE INDEX workspace_user_properties_unique_workspace_user_when_deleted_at ON workspace_user_properties USING btree (workspace_id, user_id) WHERE (deleted_at IS NULL);

