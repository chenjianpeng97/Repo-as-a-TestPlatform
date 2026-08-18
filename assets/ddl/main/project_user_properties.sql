-- auto-generated definition
create table project_user_properties
(
    created_at         timestamptz      not null,
    updated_at         timestamptz      not null,
    id                 uuid             not null
        primary key,
    display_properties jsonb            not null,
    created_by_id      uuid             null,
    project_id         uuid             not null,
    updated_by_id      uuid             null,
    user_id            uuid             not null,
    workspace_id       uuid             not null,
    display_filters    jsonb            not null,
    filters            jsonb            not null,
    deleted_at         timestamptz      null,
    rich_filters       jsonb            not null,
    preferences        jsonb            not null,
    sort_order         double precision not null
);

CREATE INDEX issue_property_created_by_id_8e92131c ON project_user_properties USING btree (created_by_id);

CREATE INDEX issue_property_project_id_30e7de7b ON project_user_properties USING btree (project_id);

CREATE INDEX issue_property_updated_by_id_ff158d4d ON project_user_properties USING btree (updated_by_id);

CREATE INDEX issue_property_user_id_0b1d1c8f ON project_user_properties USING btree (user_id);

CREATE INDEX issue_property_workspace_id_17860d65 ON project_user_properties USING btree (workspace_id);

CREATE UNIQUE INDEX issue_user_properties_user_id_project_id_delet_2217dce5_uniq ON project_user_properties USING btree (user_id, project_id, deleted_at);

CREATE UNIQUE INDEX project_user_property_unique_user_project_when_deleted_at_null ON project_user_properties USING btree (user_id, project_id) WHERE (deleted_at IS NULL);

