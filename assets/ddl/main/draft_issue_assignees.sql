-- auto-generated definition
create table draft_issue_assignees
(
    created_at     timestamptz not null,
    updated_at     timestamptz not null,
    deleted_at     timestamptz null,
    id             uuid        not null
        primary key,
    assignee_id    uuid        not null,
    created_by_id  uuid        null,
    draft_issue_id uuid        not null,
    project_id     uuid        null,
    updated_by_id  uuid        null,
    workspace_id   uuid        not null
);

CREATE INDEX draft_issue_assignees_assignee_id_9cc52f9d ON draft_issue_assignees USING btree (assignee_id);

CREATE INDEX draft_issue_assignees_created_by_id_c25d4bde ON draft_issue_assignees USING btree (created_by_id);

CREATE INDEX draft_issue_assignees_draft_issue_id_70827be2 ON draft_issue_assignees USING btree (draft_issue_id);

CREATE INDEX draft_issue_assignees_project_id_c87dd571 ON draft_issue_assignees USING btree (project_id);

CREATE INDEX draft_issue_assignees_updated_by_id_16dbb5e0 ON draft_issue_assignees USING btree (updated_by_id);

CREATE INDEX draft_issue_assignees_workspace_id_e28a98e9 ON draft_issue_assignees USING btree (workspace_id);

CREATE UNIQUE INDEX draft_issue_assignee_unique_issue_assignee_when_deleted_at_null ON draft_issue_assignees USING btree (draft_issue_id, assignee_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX draft_issue_assignees_draft_issue_id_assignee__7cd49721_uniq ON draft_issue_assignees USING btree (draft_issue_id, assignee_id, deleted_at);

-- （draft_issue_assignees 暂无数据，无示例 INSERT）
