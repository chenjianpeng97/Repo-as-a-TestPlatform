-- auto-generated definition
create table states
(
    created_at      timestamptz      not null,
    updated_at      timestamptz      not null,
    id              uuid             not null
        primary key,
    name            varchar(255)     not null,
    description     text             not null,
    color           varchar(255)     not null,
    slug            varchar(100)     not null,
    created_by_id   uuid             null,
    project_id      uuid             not null,
    updated_by_id   uuid             null,
    workspace_id    uuid             not null,
    sequence        double precision not null,
    group           varchar(20)      not null,
    default         boolean          not null,
    external_id     varchar(255)     null,
    external_source varchar(255)     null,
    is_triage       boolean          not null,
    deleted_at      timestamptz      null
);

CREATE INDEX state_created_by_id_ff51a50d ON states USING btree (created_by_id);

CREATE INDEX state_project_id_23a65fd6 ON states USING btree (project_id);

CREATE INDEX state_slug_bab0af35 ON states USING btree (slug);

CREATE INDEX state_slug_bab0af35_like ON states USING btree (slug varchar_pattern_ops);

CREATE INDEX state_updated_by_id_be298453 ON states USING btree (updated_by_id);

CREATE INDEX state_workspace_id_2293282d ON states USING btree (workspace_id);

CREATE UNIQUE INDEX state_unique_name_project_when_deleted_at_null ON states USING btree (name, project_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX states_name_project_id_deleted_at_02f90488_uniq ON states USING btree (name, project_id, deleted_at);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "states" ("created_at", "updated_at", "id", "name", "description", "color", "slug", "created_by_id", "project_id", "updated_by_id", "workspace_id", "sequence", "group", "default", "external_id", "external_source", "is_triage", "deleted_at") VALUES ('2026-08-03 12:54:47.379508+00:00', '2026-08-03 12:54:47.379510+00:00', 'ffd5480e-95a2-4521-b052-a7a78a02c3da', 'Todo', '', '#60646C', '', 'bb96a7c2-ef4b-466f-a2af-92315b642787', '9214eb9d-bc37-4cae-8a26-ea557b47d172', NULL, '82345500-e469-419d-843d-92902ffac9db', 25000.0, 'unstarted', FALSE, NULL, NULL, FALSE, NULL);
