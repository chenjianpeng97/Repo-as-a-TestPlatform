-- auto-generated definition
create table issue_description_versions
(
    created_at           timestamptz not null,
    updated_at           timestamptz not null,
    deleted_at           timestamptz null,
    id                   uuid        not null
        primary key,
    description_binary   bytea       null,
    description_html     text        not null,
    description_stripped text        null,
    description_json     jsonb       not null,
    last_saved_at        timestamptz not null,
    created_by_id        uuid        null,
    issue_id             uuid        not null,
    owned_by_id          uuid        not null,
    project_id           uuid        not null,
    updated_by_id        uuid        null,
    workspace_id         uuid        not null
);

CREATE INDEX issue_description_versions_created_by_id_3f7e62a1 ON issue_description_versions USING btree (created_by_id);

CREATE INDEX issue_description_versions_issue_id_c8baa13e ON issue_description_versions USING btree (issue_id);

CREATE INDEX issue_description_versions_owned_by_id_0effe4d0 ON issue_description_versions USING btree (owned_by_id);

CREATE INDEX issue_description_versions_project_id_536b23ef ON issue_description_versions USING btree (project_id);

CREATE INDEX issue_description_versions_updated_by_id_6530365d ON issue_description_versions USING btree (updated_by_id);

CREATE INDEX issue_description_versions_workspace_id_88e930f9 ON issue_description_versions USING btree (workspace_id);

