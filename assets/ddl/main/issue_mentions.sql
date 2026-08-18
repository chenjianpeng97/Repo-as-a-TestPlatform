-- auto-generated definition
create table issue_mentions
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    id            uuid        not null
        primary key,
    created_by_id uuid        null,
    issue_id      uuid        not null,
    mention_id    uuid        not null,
    project_id    uuid        not null,
    updated_by_id uuid        null,
    workspace_id  uuid        not null,
    deleted_at    timestamptz null
);

CREATE INDEX issue_mentions_created_by_id_eb44759e ON issue_mentions USING btree (created_by_id);

CREATE INDEX issue_mentions_issue_id_d8821107 ON issue_mentions USING btree (issue_id);

CREATE INDEX issue_mentions_mention_id_cf1b9346 ON issue_mentions USING btree (mention_id);

CREATE INDEX issue_mentions_project_id_d0cccdf5 ON issue_mentions USING btree (project_id);

CREATE INDEX issue_mentions_updated_by_id_c62106d3 ON issue_mentions USING btree (updated_by_id);

CREATE INDEX issue_mentions_workspace_id_4ca59d05 ON issue_mentions USING btree (workspace_id);

CREATE UNIQUE INDEX issue_mention_unique_issue_mention_when_deleted_at_null ON issue_mentions USING btree (issue_id, mention_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX issue_mentions_issue_id_mention_id_deleted_at_f6ecd6ed_uniq ON issue_mentions USING btree (issue_id, mention_id, deleted_at);

-- （issue_mentions 暂无数据，无示例 INSERT）
