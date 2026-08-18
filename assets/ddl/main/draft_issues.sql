-- auto-generated definition
create table draft_issues
(
    created_at           timestamptz      not null,
    updated_at           timestamptz      not null,
    deleted_at           timestamptz      null,
    id                   uuid             not null
        primary key,
    name                 varchar(255)     null,
    description_json     jsonb            not null,
    description_html     text             not null,
    description_stripped text             null,
    description_binary   bytea            null,
    priority             varchar(30)      not null,
    start_date           date             null,
    target_date          date             null,
    sort_order           double precision not null,
    completed_at         timestamptz      null,
    external_source      varchar(255)     null,
    external_id          varchar(255)     null,
    created_by_id        uuid             null,
    estimate_point_id    uuid             null,
    parent_id            uuid             null,
    project_id           uuid             null,
    state_id             uuid             null,
    type_id              uuid             null,
    updated_by_id        uuid             null,
    workspace_id         uuid             not null
);

CREATE INDEX draft_issues_created_by_id_aedba72a ON draft_issues USING btree (created_by_id);

CREATE INDEX draft_issues_estimate_point_id_9e333189 ON draft_issues USING btree (estimate_point_id);

CREATE INDEX draft_issues_parent_id_eee6ec32 ON draft_issues USING btree (parent_id);

CREATE INDEX draft_issues_project_id_784a560c ON draft_issues USING btree (project_id);

CREATE INDEX draft_issues_state_id_94f28f5a ON draft_issues USING btree (state_id);

CREATE INDEX draft_issues_type_id_7a62fe34 ON draft_issues USING btree (type_id);

CREATE INDEX draft_issues_updated_by_id_1ca3cd4e ON draft_issues USING btree (updated_by_id);

CREATE INDEX draft_issues_workspace_id_9d8512c8 ON draft_issues USING btree (workspace_id);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "draft_issues" ("created_at", "updated_at", "deleted_at", "id", "name", "description_json", "description_html", "description_stripped", "description_binary", "priority", "start_date", "target_date", "sort_order", "completed_at", "external_source", "external_id", "created_by_id", "estimate_point_id", "parent_id", "project_id", "state_id", "type_id", "updated_by_id", "workspace_id") VALUES ('2026-07-14 08:55:31.919640+00:00', '2026-07-14 08:55:31.919859+00:00', NULL, '6c4d0909-29cc-4f0c-b6ae-391f4251cc43', '测试', '{}', '<p class="editor-paragraph-block" data-id="7268892e-9f74-4b00-ac1c-7466ab07b115">第一篇</p>', '第一篇', NULL, 'none', '2026-07-15', '2026-07-19', 65535.0, NULL, NULL, NULL, '9d1f264d-7dee-48c5-ab98-087db907b8a1', NULL, NULL, 'ec840712-e7ae-41f7-bc45-ff324bee0248', '23441ef1-5c6a-4029-99fc-55e298004cd9', NULL, NULL, '6f2f3ff8-62de-4127-978b-54991c166df3');
