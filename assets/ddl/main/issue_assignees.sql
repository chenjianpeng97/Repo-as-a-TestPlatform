-- auto-generated definition
create table issue_assignees
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    id            uuid        not null
        primary key,
    assignee_id   uuid        not null,
    created_by_id uuid        null,
    issue_id      uuid        not null,
    project_id    uuid        not null,
    updated_by_id uuid        null,
    workspace_id  uuid        not null,
    deleted_at    timestamptz null
);

CREATE INDEX issue_assignee_assignee_id_50f5c04e ON issue_assignees USING btree (assignee_id);

CREATE INDEX issue_assignee_created_by_id_f693d43b ON issue_assignees USING btree (created_by_id);

CREATE INDEX issue_assignee_issue_id_72da08db ON issue_assignees USING btree (issue_id);

CREATE INDEX issue_assignee_project_id_61c18bf2 ON issue_assignees USING btree (project_id);

CREATE INDEX issue_assignee_updated_by_id_c54088aa ON issue_assignees USING btree (updated_by_id);

CREATE INDEX issue_assignee_workspace_id_9aad55b7 ON issue_assignees USING btree (workspace_id);

CREATE UNIQUE INDEX issue_assignee_unique_issue_assignee_when_deleted_at_null ON issue_assignees USING btree (issue_id, assignee_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX issue_assignees_issue_id_assignee_id_deleted_at_b2623a0e_uniq ON issue_assignees USING btree (issue_id, assignee_id, deleted_at);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "issue_assignees" ("created_at", "updated_at", "id", "assignee_id", "created_by_id", "issue_id", "project_id", "updated_by_id", "workspace_id", "deleted_at") VALUES ('2026-07-14 09:41:35.997986+00:00', '2026-07-14 09:41:35.997992+00:00', 'b488d2c4-2f86-4c0b-93f9-f500a3a6ccee', '9d1f264d-7dee-48c5-ab98-087db907b8a1', '9d1f264d-7dee-48c5-ab98-087db907b8a1', 'fd913c95-c2e4-49b0-b0ef-b68d06b55342', 'ec840712-e7ae-41f7-bc45-ff324bee0248', '9d1f264d-7dee-48c5-ab98-087db907b8a1', '6f2f3ff8-62de-4127-978b-54991c166df3', NULL);
