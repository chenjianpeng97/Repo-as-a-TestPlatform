-- auto-generated definition
create table draft_issue_cycles
(
    created_at     timestamptz not null,
    updated_at     timestamptz not null,
    deleted_at     timestamptz null,
    id             uuid        not null
        primary key,
    created_by_id  uuid        null,
    cycle_id       uuid        not null,
    draft_issue_id uuid        not null,
    project_id     uuid        null,
    updated_by_id  uuid        null,
    workspace_id   uuid        not null
);

CREATE INDEX draft_issue_cycles_created_by_id_e56335c8 ON draft_issue_cycles USING btree (created_by_id);

CREATE INDEX draft_issue_cycles_cycle_id_b214e11f ON draft_issue_cycles USING btree (cycle_id);

CREATE INDEX draft_issue_cycles_draft_issue_id_ed45e8a2 ON draft_issue_cycles USING btree (draft_issue_id);

CREATE INDEX draft_issue_cycles_project_id_dc5d1ff6 ON draft_issue_cycles USING btree (project_id);

CREATE INDEX draft_issue_cycles_updated_by_id_518a23ab ON draft_issue_cycles USING btree (updated_by_id);

CREATE INDEX draft_issue_cycles_workspace_id_4fd0aa0c ON draft_issue_cycles USING btree (workspace_id);

CREATE UNIQUE INDEX draft_issue_cycle_when_deleted_at_null ON draft_issue_cycles USING btree (draft_issue_id, cycle_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX draft_issue_cycles_draft_issue_id_cycle_id__e133e097_uniq ON draft_issue_cycles USING btree (draft_issue_id, cycle_id, deleted_at);

