-- auto-generated definition
create table cycle_issues
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    id            uuid        not null
        primary key,
    created_by_id uuid        null,
    cycle_id      uuid        not null,
    issue_id      uuid        not null,
    project_id    uuid        not null,
    updated_by_id uuid        null,
    workspace_id  uuid        not null,
    deleted_at    timestamptz null
);

CREATE INDEX cycle_issue_created_by_id_30b27539 ON cycle_issues USING btree (created_by_id);

CREATE INDEX cycle_issue_cycle_id_ec681215 ON cycle_issues USING btree (cycle_id);

CREATE INDEX cycle_issue_project_id_6ad3257a ON cycle_issues USING btree (project_id);

CREATE INDEX cycle_issue_updated_by_id_cb4516f2 ON cycle_issues USING btree (updated_by_id);

CREATE INDEX cycle_issue_workspace_id_1d77330e ON cycle_issues USING btree (workspace_id);

CREATE INDEX cycle_issues_issue_id_2d5ac97f ON cycle_issues USING btree (issue_id);

CREATE UNIQUE INDEX cycle_issue_when_deleted_at_null ON cycle_issues USING btree (cycle_id, issue_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX cycle_issues_issue_id_cycle_id_deleted_at_93e8fecd_uniq ON cycle_issues USING btree (issue_id, cycle_id, deleted_at);

