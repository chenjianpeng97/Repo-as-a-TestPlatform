-- auto-generated definition
create table workspace_themes
(
    created_at    timestamptz  not null,
    updated_at    timestamptz  not null,
    id            uuid         not null
        primary key,
    name          varchar(300) not null,
    colors        jsonb        not null,
    actor_id      uuid         not null,
    created_by_id uuid         null,
    updated_by_id uuid         null,
    workspace_id  uuid         not null,
    deleted_at    timestamptz  null
);

CREATE INDEX workspace_themes_actor_id_0e94172e ON workspace_themes USING btree (actor_id);

CREATE INDEX workspace_themes_created_by_id_676e2655 ON workspace_themes USING btree (created_by_id);

CREATE INDEX workspace_themes_updated_by_id_bba863fe ON workspace_themes USING btree (updated_by_id);

CREATE INDEX workspace_themes_workspace_id_d1bffad8 ON workspace_themes USING btree (workspace_id);

CREATE UNIQUE INDEX workspace_theme_unique_workspace_name_when_deleted_at_null ON workspace_themes USING btree (workspace_id, name) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX workspace_themes_workspace_id_name_deleted_at_b536ffd3_uniq ON workspace_themes USING btree (workspace_id, name, deleted_at);

-- （workspace_themes 暂无数据，无示例 INSERT）
