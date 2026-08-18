-- auto-generated definition
create table issue_labels
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    id            uuid        not null
        primary key,
    created_by_id uuid        null,
    issue_id      uuid        not null,
    label_id      uuid        not null,
    project_id    uuid        not null,
    updated_by_id uuid        null,
    workspace_id  uuid        not null,
    deleted_at    timestamptz null
);

CREATE INDEX issue_label_created_by_id_94075315 ON issue_labels USING btree (created_by_id);

CREATE INDEX issue_label_issue_id_0f252e52 ON issue_labels USING btree (issue_id);

CREATE INDEX issue_label_label_id_5f22777f ON issue_labels USING btree (label_id);

CREATE INDEX issue_label_project_id_eaa2ba39 ON issue_labels USING btree (project_id);

CREATE INDEX issue_label_updated_by_id_a97a6733 ON issue_labels USING btree (updated_by_id);

CREATE INDEX issue_label_workspace_id_b5b1faac ON issue_labels USING btree (workspace_id);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "issue_labels" ("created_at", "updated_at", "id", "created_by_id", "issue_id", "label_id", "project_id", "updated_by_id", "workspace_id", "deleted_at") VALUES ('2026-07-10 12:37:56.399026+00:00', '2026-07-10 12:37:56.399033+00:00', 'ed2ff30e-3266-4119-8414-26bcd26d9141', NULL, '34b8be98-89c5-4bbf-ac85-1a1e7445050c', '291d3249-5276-44d2-871d-b2efd95b6b70', 'dc06dab7-13f5-40de-9d63-79d71315d44b', NULL, '6f2f3ff8-62de-4127-978b-54991c166df3', NULL);
