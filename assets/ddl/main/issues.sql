-- auto-generated definition
create table issues
(
    created_at           timestamptz      not null,
    updated_at           timestamptz      not null,
    id                   uuid             not null
        primary key,
    name                 varchar(255)     not null,
    description_json     jsonb            not null,
    priority             varchar(30)      not null,
    start_date           date             null,
    target_date          date             null,
    sequence_id          integer          not null,
    created_by_id        uuid             null,
    parent_id            uuid             null,
    project_id           uuid             not null,
    state_id             uuid             null,
    updated_by_id        uuid             null,
    workspace_id         uuid             not null,
    description_html     text             not null,
    description_stripped text             null,
    completed_at         timestamptz      null,
    sort_order           double precision not null,
    point                integer          null,
    archived_at          date             null,
    is_draft             boolean          not null,
    external_id          varchar(255)     null,
    external_source      varchar(255)     null,
    description_binary   bytea            null,
    estimate_point_id    uuid             null,
    type_id              uuid             null,
    deleted_at           timestamptz      null
);

CREATE INDEX issue_created_by_id_8f0ae62b ON issues USING btree (created_by_id);

CREATE INDEX issue_parent_id_ce8d76ba ON issues USING btree (parent_id);

CREATE INDEX issue_project_id_fea0fc80 ON issues USING btree (project_id);

CREATE INDEX issue_state_id_1a65560d ON issues USING btree (state_id);

CREATE INDEX issue_updated_by_id_f1261863 ON issues USING btree (updated_by_id);

CREATE INDEX issue_workspace_id_c84878c1 ON issues USING btree (workspace_id);

CREATE INDEX issues_estimate_point_id_a6822abe ON issues USING btree (estimate_point_id);

CREATE INDEX issues_type_id_a4710b19 ON issues USING btree (type_id);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "issues" ("created_at", "updated_at", "id", "name", "description_json", "priority", "start_date", "target_date", "sequence_id", "created_by_id", "parent_id", "project_id", "state_id", "updated_by_id", "workspace_id", "description_html", "description_stripped", "completed_at", "sort_order", "point", "archived_at", "is_draft", "external_id", "external_source", "description_binary", "estimate_point_id", "type_id", "deleted_at") VALUES ('2026-07-14 09:40:16.226349+00:00', '2026-07-14 09:41:36.031661+00:00', 'fd913c95-c2e4-49b0-b0ef-b68d06b55342', '第一个工作项', '{}', 'urgent', '2026-07-23', '2026-07-24', 1, '9d1f264d-7dee-48c5-ab98-087db907b8a1', NULL, 'ec840712-e7ae-41f7-bc45-ff324bee0248', 'ef3ba301-2ae2-4e11-999a-c7abb86abe28', '9d1f264d-7dee-48c5-ab98-087db907b8a1', '6f2f3ff8-62de-4127-978b-54991c166df3', '<p class="editor-paragraph-block" data-id="2f30cdb7-224b-448a-a7a6-93fc9f43ba1d">descrip</p>', 'descrip', NULL, 0.0, NULL, NULL, FALSE, NULL, NULL, NULL, '9facab56-ab58-4592-a66a-80b78c0bd9a0', NULL, NULL);
