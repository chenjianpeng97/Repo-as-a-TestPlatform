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

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "testhub_project_test_repos" ("created_at", "updated_at", "deleted_at", "id", "created_by_id", "updated_by_id", "repo_url", "branch", "workdir", "last_sync_sha", "last_sync_at", "last_sync_status", "last_sync_error", "project_id", "workspace_id") VALUES ('2026-08-15 12:35:14.719877+00:00', '2026-08-17 11:44:49.549530+00:00', NULL, 'e1ea2645-8c75-49cb-b437-c68ae550e96b', '9d1f264d-7dee-48c5-ab98-087db907b8a1', NULL, '', 'sandbox/jafron', '/opt/testhub/workdir', 'c4d4bee8ba04dabe60198dd8aca56504130c249f', '2026-08-17 10:15:41.271030+00:00', 'succeeded', '', 'dc06dab7-13f5-40de-9d63-79d71315d44b', '6f2f3ff8-62de-4127-978b-54991c166df3');
