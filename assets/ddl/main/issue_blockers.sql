-- auto-generated definition
create table issue_blockers
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    id            uuid        not null
        primary key,
    block_id      uuid        not null,
    blocked_by_id uuid        not null,
    created_by_id uuid        null,
    project_id    uuid        not null,
    updated_by_id uuid        null,
    workspace_id  uuid        not null,
    deleted_at    timestamptz null
);

CREATE INDEX issue_blocker_block_id_5d15a701 ON issue_blockers USING btree (block_id);

CREATE INDEX issue_blocker_blocked_by_id_a138af71 ON issue_blockers USING btree (blocked_by_id);

CREATE INDEX issue_blocker_created_by_id_0d19f6ea ON issue_blockers USING btree (created_by_id);

CREATE INDEX issue_blocker_project_id_380bd100 ON issue_blockers USING btree (project_id);

CREATE INDEX issue_blocker_updated_by_id_4af87d63 ON issue_blockers USING btree (updated_by_id);

CREATE INDEX issue_blocker_workspace_id_419a1c71 ON issue_blockers USING btree (workspace_id);

