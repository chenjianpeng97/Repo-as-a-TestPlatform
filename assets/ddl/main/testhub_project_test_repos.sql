-- auto-generated definition
create table testhub_project_test_repos
(
    created_at       timestamptz   not null,
    updated_at       timestamptz   not null,
    deleted_at       timestamptz   null,
    id               uuid          not null
        primary key,
    created_by_id    uuid          null,
    updated_by_id    uuid          null,
    repo_url         varchar(1024) not null,
    branch           varchar(255)  not null,
    workdir          varchar(1024) not null,
    last_sync_sha    varchar(64)   not null,
    last_sync_at     timestamptz   null,
    last_sync_status varchar(32)   not null,
    last_sync_error  text          not null,
    project_id       uuid          not null,
    workspace_id     uuid          not null
);

CREATE INDEX testhub_project_test_repos_created_by_id_89b1566b ON testhub_project_test_repos USING btree (created_by_id);

CREATE INDEX testhub_project_test_repos_updated_by_id_627d3241 ON testhub_project_test_repos USING btree (updated_by_id);

CREATE INDEX testhub_project_test_repos_workspace_id_028d43cb ON testhub_project_test_repos USING btree (workspace_id);

CREATE UNIQUE INDEX testhub_project_test_repos_project_id_key ON testhub_project_test_repos USING btree (project_id);

