-- auto-generated definition
create table issue_votes
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    id            uuid        not null
        primary key,
    vote          integer     not null,
    actor_id      uuid        not null,
    created_by_id uuid        null,
    issue_id      uuid        not null,
    project_id    uuid        not null,
    updated_by_id uuid        null,
    workspace_id  uuid        not null,
    deleted_at    timestamptz null
);

CREATE INDEX issue_votes_actor_id_525cab61 ON issue_votes USING btree (actor_id);

CREATE INDEX issue_votes_created_by_id_86adcf5c ON issue_votes USING btree (created_by_id);

CREATE INDEX issue_votes_issue_id_07a61ecb ON issue_votes USING btree (issue_id);

CREATE INDEX issue_votes_project_id_b649f55b ON issue_votes USING btree (project_id);

CREATE INDEX issue_votes_updated_by_id_9e2a6cdc ON issue_votes USING btree (updated_by_id);

CREATE INDEX issue_votes_workspace_id_a3e91a6b ON issue_votes USING btree (workspace_id);

CREATE UNIQUE INDEX issue_vote_unique_issue_actor_when_deleted_at_null ON issue_votes USING btree (issue_id, actor_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX issue_votes_issue_id_actor_id_deleted_at_886f34e8_uniq ON issue_votes USING btree (issue_id, actor_id, deleted_at);

-- （issue_votes 暂无数据，无示例 INSERT）
