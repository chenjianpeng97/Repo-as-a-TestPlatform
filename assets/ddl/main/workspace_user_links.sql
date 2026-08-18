-- auto-generated definition
create table workspace_user_links
(
    created_at    timestamptz  not null,
    updated_at    timestamptz  not null,
    deleted_at    timestamptz  null,
    id            uuid         not null
        primary key,
    title         varchar(255) null,
    url           text         not null,
    metadata      jsonb        not null,
    created_by_id uuid         null,
    owner_id      uuid         not null,
    project_id    uuid         null,
    updated_by_id uuid         null,
    workspace_id  uuid         not null
);

CREATE INDEX workspace_user_links_created_by_id_b9ce7a5d ON workspace_user_links USING btree (created_by_id);

CREATE INDEX workspace_user_links_owner_id_37d99444 ON workspace_user_links USING btree (owner_id);

CREATE INDEX workspace_user_links_project_id_045e0d53 ON workspace_user_links USING btree (project_id);

CREATE INDEX workspace_user_links_updated_by_id_bd0b017f ON workspace_user_links USING btree (updated_by_id);

CREATE INDEX workspace_user_links_workspace_id_1b0a8e22 ON workspace_user_links USING btree (workspace_id);

-- （workspace_user_links 暂无数据，无示例 INSERT）
