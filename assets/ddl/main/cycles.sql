-- auto-generated definition
create table cycles
(
    created_at        timestamptz      not null,
    updated_at        timestamptz      not null,
    id                uuid             not null
        primary key,
    name              varchar(255)     not null,
    description       text             not null,
    start_date        timestamptz      null,
    end_date          timestamptz      null,
    created_by_id     uuid             null,
    owned_by_id       uuid             not null,
    project_id        uuid             not null,
    updated_by_id     uuid             null,
    workspace_id      uuid             not null,
    view_props        jsonb            not null,
    sort_order        double precision not null,
    external_id       varchar(255)     null,
    external_source   varchar(255)     null,
    progress_snapshot jsonb            not null,
    archived_at       timestamptz      null,
    logo_props        jsonb            not null,
    deleted_at        timestamptz      null,
    timezone          varchar(255)     not null,
    version           integer          not null
);

CREATE INDEX cycle_created_by_id_78e43b79 ON cycles USING btree (created_by_id);

CREATE INDEX cycle_owned_by_id_5456a4d1 ON cycles USING btree (owned_by_id);

CREATE INDEX cycle_project_id_0b590349 ON cycles USING btree (project_id);

CREATE INDEX cycle_updated_by_id_93baee43 ON cycles USING btree (updated_by_id);

CREATE INDEX cycle_workspace_id_a199e8e1 ON cycles USING btree (workspace_id);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "cycles" ("created_at", "updated_at", "id", "name", "description", "start_date", "end_date", "created_by_id", "owned_by_id", "project_id", "updated_by_id", "workspace_id", "view_props", "sort_order", "external_id", "external_source", "progress_snapshot", "archived_at", "logo_props", "deleted_at", "timezone", "version") VALUES ('2026-08-03 12:45:41.785112+00:00', '2026-08-03 12:45:41.785126+00:00', 'e87d4ff3-a5f7-469a-bb7f-fe741e87214d', 'Cycle 1: Getting Started with Plane', '', '2026-08-03 12:45:41.780922+00:00', '2026-08-17 12:45:41.780922+00:00', '284b6766-d3bb-4a5d-a14f-de5d364cc3c4', '284b6766-d3bb-4a5d-a14f-de5d364cc3c4', '20f8ab45-bce1-44c8-854c-78972f51ed62', NULL, '82345500-e469-419d-843d-92902ffac9db', '{}', 1.0, NULL, NULL, '{}', NULL, '{}', NULL, 'UTC', 1);
