-- auto-generated definition
create table issue_description_versions
(
    created_at           timestamptz not null,
    updated_at           timestamptz not null,
    deleted_at           timestamptz null,
    id                   uuid        not null
        primary key,
    description_binary   bytea       null,
    description_html     text        not null,
    description_stripped text        null,
    description_json     jsonb       not null,
    last_saved_at        timestamptz not null,
    created_by_id        uuid        null,
    issue_id             uuid        not null,
    owned_by_id          uuid        not null,
    project_id           uuid        not null,
    updated_by_id        uuid        null,
    workspace_id         uuid        not null
);

CREATE INDEX issue_description_versions_created_by_id_3f7e62a1 ON issue_description_versions USING btree (created_by_id);

CREATE INDEX issue_description_versions_issue_id_c8baa13e ON issue_description_versions USING btree (issue_id);

CREATE INDEX issue_description_versions_owned_by_id_0effe4d0 ON issue_description_versions USING btree (owned_by_id);

CREATE INDEX issue_description_versions_project_id_536b23ef ON issue_description_versions USING btree (project_id);

CREATE INDEX issue_description_versions_updated_by_id_6530365d ON issue_description_versions USING btree (updated_by_id);

CREATE INDEX issue_description_versions_workspace_id_88e930f9 ON issue_description_versions USING btree (workspace_id);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "issue_description_versions" ("created_at", "updated_at", "deleted_at", "id", "description_binary", "description_html", "description_stripped", "description_json", "last_saved_at", "created_by_id", "issue_id", "owned_by_id", "project_id", "updated_by_id", "workspace_id") VALUES ('2026-07-14 09:40:16.301709+00:00', '2026-07-14 09:40:16.301737+00:00', NULL, 'eb9d02e2-d7ef-4117-bc6c-08ee3f2dbfa4', NULL, '<p class="editor-paragraph-block" data-id="2f30cdb7-224b-448a-a7a6-93fc9f43ba1d">descrip</p>', 'descrip', '{}', '2026-07-14 09:40:16.293675+00:00', NULL, 'fd913c95-c2e4-49b0-b0ef-b68d06b55342', '9d1f264d-7dee-48c5-ab98-087db907b8a1', 'ec840712-e7ae-41f7-bc45-ff324bee0248', NULL, '6f2f3ff8-62de-4127-978b-54991c166df3');
