-- auto-generated definition
create table gitsync_project_git_remotes
(
    created_at       timestamptz   not null,
    updated_at       timestamptz   not null,
    deleted_at       timestamptz   null,
    id               uuid          not null
        primary key,
    created_by_id    uuid          null,
    updated_by_id    uuid          null,
    name             varchar(255)  not null,
    kind             varchar(32)   not null,
    workdir          varchar(1024) not null,
    host_path        varchar(1024) not null,
    repo_url         varchar(1024) not null,
    branch           varchar(255)  not null,
    credential_ref   varchar(255)  not null,
    last_sync_sha    varchar(64)   not null,
    last_sync_at     timestamptz   null,
    last_sync_status varchar(32)   not null,
    last_sync_error  text          not null,
    project_id       uuid          not null,
    workspace_id     uuid          not null
);

CREATE INDEX gitsync_pro_project_idx ON gitsync_project_git_remotes USING btree (project_id, kind);

CREATE INDEX gitsync_project_git_remotes_created_by_id_099820e6 ON gitsync_project_git_remotes USING btree (created_by_id);

CREATE INDEX gitsync_project_git_remotes_project_id_99269191 ON gitsync_project_git_remotes USING btree (project_id);

CREATE INDEX gitsync_project_git_remotes_updated_by_id_b566110b ON gitsync_project_git_remotes USING btree (updated_by_id);

CREATE INDEX gitsync_project_git_remotes_workspace_id_ccb5cd02 ON gitsync_project_git_remotes USING btree (workspace_id);

CREATE UNIQUE INDEX gitsync_remote_project_name_uniq ON gitsync_project_git_remotes USING btree (project_id, name);

