-- auto-generated definition
create table gitsync_module_bindings
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    deleted_at    timestamptz null,
    id            uuid        not null
        primary key,
    created_by_id uuid        null,
    updated_by_id uuid        null,
    module_key    varchar(64) not null,
    project_id    uuid        not null,
    workspace_id  uuid        not null,
    remote_id     uuid        not null
);

CREATE INDEX gitsync_module_bindings_created_by_id_aeede6d5 ON gitsync_module_bindings USING btree (created_by_id);

CREATE INDEX gitsync_module_bindings_project_id_f9f687c1 ON gitsync_module_bindings USING btree (project_id);

CREATE INDEX gitsync_module_bindings_remote_id_96bdc569 ON gitsync_module_bindings USING btree (remote_id);

CREATE INDEX gitsync_module_bindings_updated_by_id_3e39c10e ON gitsync_module_bindings USING btree (updated_by_id);

CREATE INDEX gitsync_module_bindings_workspace_id_448656c8 ON gitsync_module_bindings USING btree (workspace_id);

CREATE UNIQUE INDEX gitsync_binding_project_module_uniq ON gitsync_module_bindings USING btree (project_id, module_key);

