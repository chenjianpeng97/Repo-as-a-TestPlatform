-- auto-generated definition
create table draft_issue_labels
(
    created_at     timestamptz not null,
    updated_at     timestamptz not null,
    deleted_at     timestamptz null,
    id             uuid        not null
        primary key,
    created_by_id  uuid        null,
    draft_issue_id uuid        not null,
    label_id       uuid        not null,
    project_id     uuid        null,
    updated_by_id  uuid        null,
    workspace_id   uuid        not null
);

CREATE INDEX draft_issue_labels_created_by_id_88217eef ON draft_issue_labels USING btree (created_by_id);

CREATE INDEX draft_issue_labels_draft_issue_id_339d4c2b ON draft_issue_labels USING btree (draft_issue_id);

CREATE INDEX draft_issue_labels_label_id_b9b001a5 ON draft_issue_labels USING btree (label_id);

CREATE INDEX draft_issue_labels_project_id_16f9ba0a ON draft_issue_labels USING btree (project_id);

CREATE INDEX draft_issue_labels_updated_by_id_edac537c ON draft_issue_labels USING btree (updated_by_id);

CREATE INDEX draft_issue_labels_workspace_id_489a9873 ON draft_issue_labels USING btree (workspace_id);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "draft_issue_labels" ("created_at", "updated_at", "deleted_at", "id", "created_by_id", "draft_issue_id", "label_id", "project_id", "updated_by_id", "workspace_id") VALUES ('2026-07-14 08:56:07.683413+00:00', '2026-07-14 08:56:07.683428+00:00', NULL, '8611eb43-6a21-461a-a101-54ac25c98ee9', '9d1f264d-7dee-48c5-ab98-087db907b8a1', '678afc8f-dfd3-4393-b883-64d3ba6571e0', '03f416f2-64f1-4f71-b321-6f4a07e14d14', 'ec840712-e7ae-41f7-bc45-ff324bee0248', NULL, '6f2f3ff8-62de-4127-978b-54991c166df3');
