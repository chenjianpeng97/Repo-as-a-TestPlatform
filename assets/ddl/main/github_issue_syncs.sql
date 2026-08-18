-- auto-generated definition
create table github_issue_syncs
(
    created_at         timestamptz  not null,
    updated_at         timestamptz  not null,
    id                 uuid         not null
        primary key,
    repo_issue_id      bigint       not null,
    github_issue_id    bigint       not null,
    issue_url          varchar(200) not null,
    created_by_id      uuid         null,
    issue_id           uuid         not null,
    project_id         uuid         not null,
    repository_sync_id uuid         not null,
    updated_by_id      uuid         null,
    workspace_id       uuid         not null,
    deleted_at         timestamptz  null
);

CREATE INDEX github_issue_syncs_created_by_id_d02b7c56 ON github_issue_syncs USING btree (created_by_id);

CREATE INDEX github_issue_syncs_issue_id_450cb083 ON github_issue_syncs USING btree (issue_id);

CREATE INDEX github_issue_syncs_project_id_4609ad0c ON github_issue_syncs USING btree (project_id);

CREATE INDEX github_issue_syncs_repository_sync_id_ba0d4de4 ON github_issue_syncs USING btree (repository_sync_id);

CREATE INDEX github_issue_syncs_updated_by_id_e9cd6f86 ON github_issue_syncs USING btree (updated_by_id);

CREATE INDEX github_issue_syncs_workspace_id_eae020ad ON github_issue_syncs USING btree (workspace_id);

CREATE UNIQUE INDEX github_issue_syncs_repository_sync_id_issue_id_4b34427e_uniq ON github_issue_syncs USING btree (repository_sync_id, issue_id);

