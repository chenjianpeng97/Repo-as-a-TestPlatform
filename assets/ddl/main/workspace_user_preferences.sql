-- auto-generated definition
create table workspace_user_preferences
(
    created_at    timestamptz      not null,
    updated_at    timestamptz      not null,
    deleted_at    timestamptz      null,
    id            uuid             not null
        primary key,
    key           varchar(255)     not null,
    is_pinned     boolean          not null,
    sort_order    double precision not null,
    created_by_id uuid             null,
    updated_by_id uuid             null,
    user_id       uuid             not null,
    workspace_id  uuid             not null
);

CREATE INDEX workspace_user_preferences_created_by_id_2d566570 ON workspace_user_preferences USING btree (created_by_id);

CREATE INDEX workspace_user_preferences_updated_by_id_65fed266 ON workspace_user_preferences USING btree (updated_by_id);

CREATE INDEX workspace_user_preferences_user_id_0ba5007a ON workspace_user_preferences USING btree (user_id);

CREATE INDEX workspace_user_preferences_workspace_id_a345adde ON workspace_user_preferences USING btree (workspace_id);

CREATE UNIQUE INDEX workspace_user_preferenc_workspace_id_user_id_key_79341493_uniq ON workspace_user_preferences USING btree (workspace_id, user_id, key, deleted_at);

CREATE UNIQUE INDEX workspace_user_preferences_unique_workspace_user_key_when_delet ON workspace_user_preferences USING btree (workspace_id, user_id, key) WHERE (deleted_at IS NULL);

