-- auto-generated definition
create table workspace_home_preferences
(
    created_at    timestamptz      not null,
    updated_at    timestamptz      not null,
    deleted_at    timestamptz      null,
    id            uuid             not null
        primary key,
    key           varchar(255)     not null,
    is_enabled    boolean          not null,
    config        jsonb            not null,
    created_by_id uuid             null,
    updated_by_id uuid             null,
    user_id       uuid             not null,
    workspace_id  uuid             not null,
    sort_order    double precision not null
);

CREATE INDEX workspace_home_preferences_created_by_id_f31fc163 ON workspace_home_preferences USING btree (created_by_id);

CREATE INDEX workspace_home_preferences_updated_by_id_14ed118a ON workspace_home_preferences USING btree (updated_by_id);

CREATE INDEX workspace_home_preferences_user_id_4087938d ON workspace_home_preferences USING btree (user_id);

CREATE INDEX workspace_home_preferences_workspace_id_b49f76e0 ON workspace_home_preferences USING btree (workspace_id);

CREATE UNIQUE INDEX workspace_home_preferenc_workspace_id_user_id_key_75ea36d3_uniq ON workspace_home_preferences USING btree (workspace_id, user_id, key, deleted_at);

CREATE UNIQUE INDEX workspace_user_home_preferences_unique_workspace_user_key_when_ ON workspace_home_preferences USING btree (workspace_id, user_id, key) WHERE (deleted_at IS NULL);

