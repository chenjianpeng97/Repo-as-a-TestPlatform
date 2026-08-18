-- auto-generated definition
create table estimate_points
(
    created_at    timestamptz  not null,
    updated_at    timestamptz  not null,
    id            uuid         not null
        primary key,
    key           integer      not null,
    description   text         not null,
    value         varchar(255) not null,
    created_by_id uuid         null,
    estimate_id   uuid         not null,
    project_id    uuid         not null,
    updated_by_id uuid         null,
    workspace_id  uuid         not null,
    deleted_at    timestamptz  null
);

CREATE INDEX estimate_points_created_by_id_d1b04bd9 ON estimate_points USING btree (created_by_id);

CREATE INDEX estimate_points_estimate_id_4b4cb706 ON estimate_points USING btree (estimate_id);

CREATE INDEX estimate_points_project_id_ba9bcb2c ON estimate_points USING btree (project_id);

CREATE INDEX estimate_points_updated_by_id_a1da94e1 ON estimate_points USING btree (updated_by_id);

CREATE INDEX estimate_points_workspace_id_96fc4f92 ON estimate_points USING btree (workspace_id);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "estimate_points" ("created_at", "updated_at", "id", "key", "description", "value", "created_by_id", "estimate_id", "project_id", "updated_by_id", "workspace_id", "deleted_at") VALUES ('2026-07-14 09:39:46.073838+00:00', '2026-07-14 09:39:46.073839+00:00', 'fa346140-e324-4a0d-9ee0-6e1b0079e3c0', 6, '', '13', '9d1f264d-7dee-48c5-ab98-087db907b8a1', '9af23408-ce13-41b0-9f7e-61f9325c6ecb', 'ec840712-e7ae-41f7-bc45-ff324bee0248', '9d1f264d-7dee-48c5-ab98-087db907b8a1', '6f2f3ff8-62de-4127-978b-54991c166df3', NULL);
