-- auto-generated definition
create table user_notification_preferences
(
    created_at      timestamptz not null,
    updated_at      timestamptz not null,
    id              uuid        not null
        primary key,
    property_change boolean     not null,
    state_change    boolean     not null,
    comment         boolean     not null,
    mention         boolean     not null,
    issue_completed boolean     not null,
    created_by_id   uuid        null,
    project_id      uuid        null,
    updated_by_id   uuid        null,
    user_id         uuid        not null,
    workspace_id    uuid        null,
    deleted_at      timestamptz null
);

CREATE INDEX user_notification_preferences_created_by_id_54dc743a ON user_notification_preferences USING btree (created_by_id);

CREATE INDEX user_notification_preferences_project_id_e0ca17f8 ON user_notification_preferences USING btree (project_id);

CREATE INDEX user_notification_preferences_updated_by_id_eb70a86d ON user_notification_preferences USING btree (updated_by_id);

CREATE INDEX user_notification_preferences_user_id_9dccc056 ON user_notification_preferences USING btree (user_id);

CREATE INDEX user_notification_preferences_workspace_id_a2321c58 ON user_notification_preferences USING btree (workspace_id);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "user_notification_preferences" ("created_at", "updated_at", "id", "property_change", "state_change", "comment", "mention", "issue_completed", "created_by_id", "project_id", "updated_by_id", "user_id", "workspace_id", "deleted_at") VALUES ('2026-07-10 12:35:44.200544+00:00', '2026-07-10 12:35:44.200554+00:00', 'c63defe5-6c2d-4ac4-9ab6-76ed926270c3', TRUE, TRUE, TRUE, TRUE, TRUE, NULL, NULL, NULL, '9d1f264d-7dee-48c5-ab98-087db907b8a1', NULL, NULL);
