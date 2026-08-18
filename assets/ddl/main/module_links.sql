-- auto-generated definition
create table module_links
(
    created_at    timestamptz  not null,
    updated_at    timestamptz  not null,
    id            uuid         not null
        primary key,
    title         varchar(255) null,
    url           varchar(200) not null,
    created_by_id uuid         null,
    module_id     uuid         not null,
    project_id    uuid         not null,
    updated_by_id uuid         null,
    workspace_id  uuid         not null,
    metadata      jsonb        not null,
    deleted_at    timestamptz  null
);

CREATE INDEX module_links_created_by_id_eaf6492f ON module_links USING btree (created_by_id);

CREATE INDEX module_links_module_id_0fda3f8a ON module_links USING btree (module_id);

CREATE INDEX module_links_project_id_f720bb79 ON module_links USING btree (project_id);

CREATE INDEX module_links_updated_by_id_4da419e7 ON module_links USING btree (updated_by_id);

CREATE INDEX module_links_workspace_id_0521c11c ON module_links USING btree (workspace_id);

