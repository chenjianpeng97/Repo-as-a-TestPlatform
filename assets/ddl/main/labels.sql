-- auto-generated definition
create table labels
(
    created_at      timestamptz      not null,
    updated_at      timestamptz      not null,
    id              uuid             not null
        primary key,
    name            varchar(255)     not null,
    description     text             not null,
    created_by_id   uuid             null,
    project_id      uuid             null,
    updated_by_id   uuid             null,
    workspace_id    uuid             not null,
    parent_id       uuid             null,
    color           varchar(255)     not null,
    sort_order      double precision not null,
    external_id     varchar(255)     null,
    external_source varchar(255)     null,
    deleted_at      timestamptz      null
);

CREATE INDEX label_created_by_id_aa6ffcfa ON labels USING btree (created_by_id);

CREATE INDEX label_parent_id_7a853296 ON labels USING btree (parent_id);

CREATE INDEX label_project_id_90e0f1a2 ON labels USING btree (project_id);

CREATE INDEX label_updated_by_id_894a5464 ON labels USING btree (updated_by_id);

CREATE INDEX label_workspace_id_c4c9ae5a ON labels USING btree (workspace_id);

CREATE UNIQUE INDEX unique_name_when_project_null_and_not_deleted ON labels USING btree (name) WHERE ((deleted_at IS NULL) AND (project_id IS NULL));

CREATE UNIQUE INDEX unique_project_name_when_not_deleted ON labels USING btree (project_id, name) WHERE ((deleted_at IS NULL) AND (project_id IS NOT NULL));

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "labels" ("created_at", "updated_at", "id", "name", "description", "created_by_id", "project_id", "updated_by_id", "workspace_id", "parent_id", "color", "sort_order", "external_id", "external_source", "deleted_at") VALUES ('2026-07-10 12:37:56.253773+00:00', '2026-07-10 12:37:56.253785+00:00', 'cf1ba6f4-ffd3-4265-b860-f9d3ab08d603', 'admin', '', '7f979bbb-cc06-4739-a6bb-0348e80efda7', 'dc06dab7-13f5-40de-9d63-79d71315d44b', NULL, '6f2f3ff8-62de-4127-978b-54991c166df3', NULL, '#0693e3', 85535.0, NULL, NULL, NULL);
