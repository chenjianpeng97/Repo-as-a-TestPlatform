-- auto-generated definition
create table estimates
(
    created_at    timestamptz  not null,
    updated_at    timestamptz  not null,
    id            uuid         not null
        primary key,
    name          varchar(255) not null,
    description   text         not null,
    created_by_id uuid         null,
    project_id    uuid         not null,
    updated_by_id uuid         null,
    workspace_id  uuid         not null,
    type          varchar(255) not null,
    last_used     boolean      not null,
    deleted_at    timestamptz  null
);

CREATE INDEX estimates_created_by_id_7e401493 ON estimates USING btree (created_by_id);

CREATE INDEX estimates_project_id_7f195a41 ON estimates USING btree (project_id);

CREATE INDEX estimates_updated_by_id_b3fcfb1d ON estimates USING btree (updated_by_id);

CREATE INDEX estimates_workspace_id_718811eb ON estimates USING btree (workspace_id);

CREATE UNIQUE INDEX estimate_unique_name_project_when_deleted_at_null ON estimates USING btree (name, project_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX estimates_name_project_id_deleted_at_41d66639_uniq ON estimates USING btree (name, project_id, deleted_at);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "estimates" ("created_at", "updated_at", "id", "name", "description", "created_by_id", "project_id", "updated_by_id", "workspace_id", "type", "last_used", "deleted_at") VALUES ('2026-07-14 09:39:46.067905+00:00', '2026-07-14 09:39:46.067915+00:00', '9af23408-ce13-41b0-9f7e-61f9325c6ecb', 'Points', '', '9d1f264d-7dee-48c5-ab98-087db907b8a1', 'ec840712-e7ae-41f7-bc45-ff324bee0248', NULL, '6f2f3ff8-62de-4127-978b-54991c166df3', 'points', TRUE, NULL);
