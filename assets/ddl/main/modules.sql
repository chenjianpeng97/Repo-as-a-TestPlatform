-- auto-generated definition
create table modules
(
    created_at       timestamptz      not null,
    updated_at       timestamptz      not null,
    id               uuid             not null
        primary key,
    name             varchar(255)     not null,
    description      text             not null,
    description_text jsonb            null,
    description_html jsonb            null,
    start_date       date             null,
    target_date      date             null,
    status           varchar(20)      not null,
    created_by_id    uuid             null,
    lead_id          uuid             null,
    project_id       uuid             not null,
    updated_by_id    uuid             null,
    workspace_id     uuid             not null,
    view_props       jsonb            not null,
    sort_order       double precision not null,
    external_id      varchar(255)     null,
    external_source  varchar(255)     null,
    archived_at      timestamptz      null,
    logo_props       jsonb            not null,
    deleted_at       timestamptz      null
);

CREATE INDEX module_created_by_id_ff7a5866 ON modules USING btree (created_by_id);

CREATE INDEX module_lead_id_04966630 ON modules USING btree (lead_id);

CREATE INDEX module_project_id_da84b04f ON modules USING btree (project_id);

CREATE INDEX module_updated_by_id_72ab6d5c ON modules USING btree (updated_by_id);

CREATE INDEX module_workspace_id_0a826fef ON modules USING btree (workspace_id);

CREATE UNIQUE INDEX module_unique_name_project_when_deleted_at_null ON modules USING btree (name, project_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX modules_name_project_id_deleted_at_328e2346_uniq ON modules USING btree (name, project_id, deleted_at);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "modules" ("created_at", "updated_at", "id", "name", "description", "description_text", "description_html", "start_date", "target_date", "status", "created_by_id", "lead_id", "project_id", "updated_by_id", "workspace_id", "view_props", "sort_order", "external_id", "external_source", "archived_at", "logo_props", "deleted_at") VALUES ('2026-08-03 12:45:41.807292+00:00', '2026-08-03 12:45:41.807302+00:00', 'eb61034e-cb9e-4182-95a1-a19f3b41f6db', 'Onboarding Flow (Feature)', 'Everything about getting started - creating a project, inviting teammates.', NULL, NULL, '2026-08-05', '2026-08-19', 'backlog', '284b6766-d3bb-4a5d-a14f-de5d364cc3c4', NULL, '20f8ab45-bce1-44c8-854c-78972f51ed62', NULL, '82345500-e469-419d-843d-92902ffac9db', '{}', -9999.0, NULL, NULL, NULL, '{}', NULL);
