-- auto-generated definition
create table github_repositories
(
    created_at    timestamptz  not null,
    updated_at    timestamptz  not null,
    id            uuid         not null
        primary key,
    name          varchar(500) not null,
    url           varchar(200) null,
    config        jsonb        not null,
    repository_id bigint       not null,
    owner         varchar(500) not null,
    created_by_id uuid         null,
    project_id    uuid         not null,
    updated_by_id uuid         null,
    workspace_id  uuid         not null,
    deleted_at    timestamptz  null
);

CREATE INDEX github_repositories_created_by_id_104fa685 ON github_repositories USING btree (created_by_id);

CREATE INDEX github_repositories_project_id_65c546bb ON github_repositories USING btree (project_id);

CREATE INDEX github_repositories_updated_by_id_8aa4d772 ON github_repositories USING btree (updated_by_id);

CREATE INDEX github_repositories_workspace_id_c4de7326 ON github_repositories USING btree (workspace_id);

-- （github_repositories 暂无数据，无示例 INSERT）
