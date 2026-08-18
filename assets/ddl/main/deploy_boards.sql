-- auto-generated definition
create table deploy_boards
(
    created_at           timestamptz  not null,
    updated_at           timestamptz  not null,
    id                   uuid         not null
        primary key,
    entity_identifier    uuid         null,
    entity_name          varchar(30)  null,
    anchor               varchar(255) not null,
    is_comments_enabled  boolean      not null,
    is_reactions_enabled boolean      not null,
    is_votes_enabled     boolean      not null,
    view_props           jsonb        not null,
    created_by_id        uuid         null,
    intake_id            uuid         null,
    project_id           uuid         null,
    updated_by_id        uuid         null,
    workspace_id         uuid         not null,
    deleted_at           timestamptz  null,
    is_activity_enabled  boolean      not null,
    is_disabled          boolean      not null
);

CREATE INDEX deploy_boards_anchor_fe87f323_like ON deploy_boards USING btree (anchor varchar_pattern_ops);

CREATE INDEX deploy_boards_created_by_id_149dff93 ON deploy_boards USING btree (created_by_id);

CREATE INDEX deploy_boards_inbox_id_ebc13d44 ON deploy_boards USING btree (intake_id);

CREATE INDEX deploy_boards_project_id_cfc792a1 ON deploy_boards USING btree (project_id);

CREATE INDEX deploy_boards_updated_by_id_db7ae24f ON deploy_boards USING btree (updated_by_id);

CREATE INDEX deploy_boards_workspace_id_fcf03158 ON deploy_boards USING btree (workspace_id);

CREATE UNIQUE INDEX deploy_board_unique_entity_name_entity_identifier_when_deleted_ ON deploy_boards USING btree (entity_name, entity_identifier) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX deploy_boards_anchor_key ON deploy_boards USING btree (anchor);

CREATE UNIQUE INDEX deploy_boards_entity_name_entity_ident_800ce160_uniq ON deploy_boards USING btree (entity_name, entity_identifier, deleted_at);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "deploy_boards" ("created_at", "updated_at", "id", "entity_identifier", "entity_name", "anchor", "is_comments_enabled", "is_reactions_enabled", "is_votes_enabled", "view_props", "created_by_id", "intake_id", "project_id", "updated_by_id", "workspace_id", "deleted_at", "is_activity_enabled", "is_disabled") VALUES ('2026-07-14 08:58:55.386045+00:00', '2026-07-14 08:58:55.394786+00:00', '1001d6a4-2c9b-420b-a22c-99d120d45ec8', 'ec840712-e7ae-41f7-bc45-ff324bee0248', 'project', '3e0394e8ed454422ab8b233e181f6817', FALSE, FALSE, FALSE, '{''list'': True, ''gantt'': True, ''kanban'': True, ''calendar'': True, ''spreadsheet'': True}', '9d1f264d-7dee-48c5-ab98-087db907b8a1', NULL, 'ec840712-e7ae-41f7-bc45-ff324bee0248', '9d1f264d-7dee-48c5-ab98-087db907b8a1', '6f2f3ff8-62de-4127-978b-54991c166df3', NULL, TRUE, FALSE);
