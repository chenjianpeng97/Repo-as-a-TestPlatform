-- auto-generated definition
create table projects
(
    created_at               timestamptz  not null,
    updated_at               timestamptz  not null,
    id                       uuid         not null
        primary key,
    name                     varchar(255) not null,
    description              text         not null,
    description_text         jsonb        null,
    description_html         jsonb        null,
    network                  smallint     not null,
    identifier               varchar(12)  not null,
    created_by_id            uuid         null,
    default_assignee_id      uuid         null,
    project_lead_id          uuid         null,
    updated_by_id            uuid         null,
    workspace_id             uuid         not null,
    emoji                    varchar(255) null,
    cycle_view               boolean      not null,
    module_view              boolean      not null,
    cover_image              text         null,
    issue_views_view         boolean      not null,
    page_view                boolean      not null,
    estimate_id              uuid         null,
    icon_prop                jsonb        null,
    intake_view              boolean      not null,
    archive_in               integer      not null,
    close_in                 integer      not null,
    default_state_id         uuid         null,
    logo_props               jsonb        not null,
    archived_at              timestamptz  null,
    is_time_tracking_enabled boolean      not null,
    is_issue_type_enabled    boolean      not null,
    deleted_at               timestamptz  null,
    guest_view_all_features  boolean      not null,
    timezone                 varchar(255) not null,
    cover_image_asset_id     uuid         null,
    external_id              varchar(255) null,
    external_source          varchar(255) null
);

CREATE INDEX project_created_by_id_6cc13408 ON projects USING btree (created_by_id);

CREATE INDEX project_default_assignee_id_6ba45f90 ON projects USING btree (default_assignee_id);

CREATE INDEX project_project_lead_id_caf8e353 ON projects USING btree (project_lead_id);

CREATE INDEX project_updated_by_id_fe290525 ON projects USING btree (updated_by_id);

CREATE INDEX project_workspace_id_01764ff9 ON projects USING btree (workspace_id);

CREATE INDEX projects_cover_image_asset_id_e6636b92 ON projects USING btree (cover_image_asset_id);

CREATE INDEX projects_default_state_id_f13e8b95 ON projects USING btree (default_state_id);

CREATE INDEX projects_estimate_id_85c7b2ac ON projects USING btree (estimate_id);

CREATE INDEX projects_identifier_3267ade8 ON projects USING btree (identifier);

CREATE INDEX projects_identifier_3267ade8_like ON projects USING btree (identifier varchar_pattern_ops);

CREATE UNIQUE INDEX project_unique_identifier_workspace_when_deleted_at_null ON projects USING btree (identifier, workspace_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX project_unique_name_workspace_when_deleted_at_null ON projects USING btree (name, workspace_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX projects_identifier_workspace_id_deleted_at_7d2fa8c1_uniq ON projects USING btree (identifier, workspace_id, deleted_at);

CREATE UNIQUE INDEX projects_name_workspace_id_deleted_at_c7aa56f7_uniq ON projects USING btree (name, workspace_id, deleted_at);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "projects" ("created_at", "updated_at", "id", "name", "description", "description_text", "description_html", "network", "identifier", "created_by_id", "default_assignee_id", "project_lead_id", "updated_by_id", "workspace_id", "emoji", "cycle_view", "module_view", "cover_image", "issue_views_view", "page_view", "estimate_id", "icon_prop", "intake_view", "archive_in", "close_in", "default_state_id", "logo_props", "archived_at", "is_time_tracking_enabled", "is_issue_type_enabled", "deleted_at", "guest_view_all_features", "timezone", "cover_image_asset_id", "external_id", "external_source") VALUES ('2026-07-10 12:38:41.533946+00:00', '2026-07-14 09:39:53.142566+00:00', 'ec840712-e7ae-41f7-bc45-ff324bee0248', 'first project', '', NULL, NULL, 2, 'FIRSTPROJE', '9d1f264d-7dee-48c5-ab98-087db907b8a1', NULL, NULL, '9d1f264d-7dee-48c5-ab98-087db907b8a1', '6f2f3ff8-62de-4127-978b-54991c166df3', NULL, TRUE, TRUE, NULL, TRUE, TRUE, '9af23408-ce13-41b0-9f7e-61f9325c6ecb', NULL, TRUE, 1, 12, 'c3514c85-e5ab-4b5e-b5ea-6993843cec58', '{''emoji'': {''value'': ''8986''}, ''in_use'': ''emoji''}', NULL, FALSE, FALSE, NULL, FALSE, 'UTC', NULL, NULL, NULL);
