-- auto-generated definition
create table user_recent_visits
(
    created_at        timestamptz not null,
    updated_at        timestamptz not null,
    id                uuid        not null
        primary key,
    entity_identifier uuid        null,
    entity_name       varchar(30) not null,
    visited_at        timestamptz not null,
    created_by_id     uuid        null,
    project_id        uuid        null,
    updated_by_id     uuid        null,
    user_id           uuid        not null,
    workspace_id      uuid        not null,
    deleted_at        timestamptz null
);

CREATE INDEX user_recent_visits_created_by_id_a655b75f ON user_recent_visits USING btree (created_by_id);

CREATE INDEX user_recent_visits_project_id_e5eecf27 ON user_recent_visits USING btree (project_id);

CREATE INDEX user_recent_visits_updated_by_id_42b12ef2 ON user_recent_visits USING btree (updated_by_id);

CREATE INDEX user_recent_visits_user_id_f5153288 ON user_recent_visits USING btree (user_id);

CREATE INDEX user_recent_visits_workspace_id_362a4e80 ON user_recent_visits USING btree (workspace_id);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "user_recent_visits" ("created_at", "updated_at", "id", "entity_identifier", "entity_name", "visited_at", "created_by_id", "project_id", "updated_by_id", "user_id", "workspace_id", "deleted_at") VALUES ('2026-07-14 09:15:52.469267+00:00', '2026-07-14 09:15:52.469279+00:00', 'fada0083-eb96-42df-bec7-3160e8953e32', '9016a423-429b-436d-963d-fe78cf14ec8f', 'issue', '2026-07-14 09:15:52.469292+00:00', NULL, 'dc06dab7-13f5-40de-9d63-79d71315d44b', NULL, '9d1f264d-7dee-48c5-ab98-087db907b8a1', '6f2f3ff8-62de-4127-978b-54991c166df3', NULL);
