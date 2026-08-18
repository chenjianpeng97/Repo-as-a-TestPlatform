-- auto-generated definition
create table github_comment_syncs
(
    created_at      timestamptz not null,
    updated_at      timestamptz not null,
    id              uuid        not null
        primary key,
    repo_comment_id bigint      not null,
    comment_id      uuid        not null,
    created_by_id   uuid        null,
    issue_sync_id   uuid        not null,
    project_id      uuid        not null,
    updated_by_id   uuid        null,
    workspace_id    uuid        not null,
    deleted_at      timestamptz null
);

CREATE INDEX github_comment_syncs_comment_id_6feec6d1 ON github_comment_syncs USING btree (comment_id);

CREATE INDEX github_comment_syncs_created_by_id_b1ef2517 ON github_comment_syncs USING btree (created_by_id);

CREATE INDEX github_comment_syncs_issue_sync_id_5e738eb5 ON github_comment_syncs USING btree (issue_sync_id);

CREATE INDEX github_comment_syncs_project_id_6d199ace ON github_comment_syncs USING btree (project_id);

CREATE INDEX github_comment_syncs_updated_by_id_bb05c066 ON github_comment_syncs USING btree (updated_by_id);

CREATE INDEX github_comment_syncs_workspace_id_b54528c8 ON github_comment_syncs USING btree (workspace_id);

CREATE UNIQUE INDEX github_comment_syncs_issue_sync_id_comment_id_38c82e7b_uniq ON github_comment_syncs USING btree (issue_sync_id, comment_id);

