-- auto-generated definition
create table description_versions
(
    created_at           timestamptz not null,
    updated_at           timestamptz not null,
    deleted_at           timestamptz null,
    id                   uuid        not null
        primary key,
    description_json     jsonb       not null,
    description_html     text        not null,
    description_binary   bytea       null,
    description_stripped text        null,
    created_by_id        uuid        null,
    description_id       uuid        not null,
    project_id           uuid        null,
    updated_by_id        uuid        null,
    workspace_id         uuid        not null
);

CREATE INDEX description_versions_created_by_id_6633a3de ON description_versions USING btree (created_by_id);

CREATE INDEX description_versions_description_id_dc7f19b6 ON description_versions USING btree (description_id);

CREATE INDEX description_versions_project_id_1a6c9aa9 ON description_versions USING btree (project_id);

CREATE INDEX description_versions_updated_by_id_8b5179ae ON description_versions USING btree (updated_by_id);

CREATE INDEX description_versions_workspace_id_52857186 ON description_versions USING btree (workspace_id);

