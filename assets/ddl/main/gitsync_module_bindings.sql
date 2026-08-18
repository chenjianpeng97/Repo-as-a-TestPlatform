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

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "gitsync_module_bindings" ("created_at", "updated_at", "deleted_at", "id", "created_by_id", "updated_by_id", "module_key", "project_id", "workspace_id", "remote_id") VALUES ('2026-08-17 11:44:49.554214+00:00', '2026-08-17 11:44:49.554224+00:00', NULL, 'd6237ce1-a7f4-49da-a0c8-3e59e9e0d9bc', NULL, NULL, 'features', 'dc06dab7-13f5-40de-9d63-79d71315d44b', '6f2f3ff8-62de-4127-978b-54991c166df3', '7495e822-1ef0-4fe1-a7dd-3c75fda9ce22');
