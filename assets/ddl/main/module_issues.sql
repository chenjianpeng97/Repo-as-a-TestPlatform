-- auto-generated definition
create table module_issues
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    id            uuid        not null
        primary key,
    created_by_id uuid        null,
    issue_id      uuid        not null,
    module_id     uuid        not null,
    project_id    uuid        not null,
    updated_by_id uuid        null,
    workspace_id  uuid        not null,
    deleted_at    timestamptz null
);

CREATE INDEX module_issues_created_by_id_de0b995a ON module_issues USING btree (created_by_id);

CREATE INDEX module_issues_issue_id_7caa908b ON module_issues USING btree (issue_id);

CREATE INDEX module_issues_module_id_74e0ed5a ON module_issues USING btree (module_id);

CREATE INDEX module_issues_project_id_59836d1e ON module_issues USING btree (project_id);

CREATE INDEX module_issues_updated_by_id_46dbf724 ON module_issues USING btree (updated_by_id);

CREATE INDEX module_issues_workspace_id_6bf85201 ON module_issues USING btree (workspace_id);

CREATE UNIQUE INDEX module_issue_unique_issue_module_when_deleted_at_null ON module_issues USING btree (issue_id, module_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX module_issues_issue_id_module_id_deleted_at_f944f7c9_uniq ON module_issues USING btree (issue_id, module_id, deleted_at);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "module_issues" ("created_at", "updated_at", "id", "created_by_id", "issue_id", "module_id", "project_id", "updated_by_id", "workspace_id", "deleted_at") VALUES ('2026-07-10 12:37:56.404883+00:00', '2026-07-10 12:37:56.404888+00:00', 'fdc52a3d-4a65-4104-abaa-c6c559e83216', NULL, '34b8be98-89c5-4bbf-ac85-1a1e7445050c', '4f9a5eb0-949c-47e9-9a97-738eba209bd2', 'dc06dab7-13f5-40de-9d63-79d71315d44b', NULL, '6f2f3ff8-62de-4127-978b-54991c166df3', NULL);
