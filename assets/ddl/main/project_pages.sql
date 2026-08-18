-- auto-generated definition
create table project_pages
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    id            uuid        not null
        primary key,
    created_by_id uuid        null,
    page_id       uuid        not null,
    project_id    uuid        not null,
    updated_by_id uuid        null,
    workspace_id  uuid        not null,
    deleted_at    timestamptz null
);

CREATE INDEX project_pages_created_by_id_b9d02062 ON project_pages USING btree (created_by_id);

CREATE INDEX project_pages_page_id_a0f54439 ON project_pages USING btree (page_id);

CREATE INDEX project_pages_project_id_376ba35a ON project_pages USING btree (project_id);

CREATE INDEX project_pages_updated_by_id_b80bf0f4 ON project_pages USING btree (updated_by_id);

CREATE INDEX project_pages_workspace_id_13ed9e73 ON project_pages USING btree (workspace_id);

CREATE UNIQUE INDEX project_page_unique_project_page_when_deleted_at_null ON project_pages USING btree (project_id, page_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX project_pages_project_id_page_id_deleted_at_7c80a40c_uniq ON project_pages USING btree (project_id, page_id, deleted_at);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "project_pages" ("created_at", "updated_at", "id", "created_by_id", "page_id", "project_id", "updated_by_id", "workspace_id", "deleted_at") VALUES ('2026-07-14 09:16:17.584750+00:00', '2026-07-14 09:16:17.584762+00:00', 'e64cd6b3-2b0b-47c1-840a-9b61284ab3eb', '9d1f264d-7dee-48c5-ab98-087db907b8a1', 'a0d8ecc3-6557-4945-be94-f0e3c1ce6af3', 'ec840712-e7ae-41f7-bc45-ff324bee0248', NULL, '6f2f3ff8-62de-4127-978b-54991c166df3', NULL);
