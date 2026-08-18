-- auto-generated definition
create table issue_sequences
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    id            uuid        not null
        primary key,
    sequence      bigint      not null,
    deleted       boolean     not null,
    created_by_id uuid        null,
    issue_id      uuid        null,
    project_id    uuid        not null,
    updated_by_id uuid        null,
    workspace_id  uuid        not null,
    deleted_at    timestamptz null
);

CREATE INDEX issue_sequence_created_by_id_59270506 ON issue_sequences USING btree (created_by_id);

CREATE INDEX issue_sequence_issue_id_16e9f00f ON issue_sequences USING btree (issue_id);

CREATE INDEX issue_sequence_project_id_ce882e85 ON issue_sequences USING btree (project_id);

CREATE INDEX issue_sequence_updated_by_id_310c8dd3 ON issue_sequences USING btree (updated_by_id);

CREATE INDEX issue_sequence_workspace_id_0d3f0fd4 ON issue_sequences USING btree (workspace_id);

CREATE INDEX issue_sequences_sequence_2c9458d4 ON issue_sequences USING btree (sequence);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "issue_sequences" ("created_at", "updated_at", "id", "sequence", "deleted", "created_by_id", "issue_id", "project_id", "updated_by_id", "workspace_id", "deleted_at") VALUES ('2026-07-10 12:37:56.388913+00:00', '2026-07-10 12:37:56.388918+00:00', 'fed1f28d-76d9-4b14-9b90-d13098bb4997', 4, FALSE, NULL, '34b8be98-89c5-4bbf-ac85-1a1e7445050c', 'dc06dab7-13f5-40de-9d63-79d71315d44b', NULL, '6f2f3ff8-62de-4127-978b-54991c166df3', NULL);
