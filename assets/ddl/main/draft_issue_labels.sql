-- auto-generated definition
create table draft_issue_labels
(
    created_at     timestamptz not null,
    updated_at     timestamptz not null,
    deleted_at     timestamptz null,
    id             uuid        not null
        primary key,
    created_by_id  uuid        null,
    draft_issue_id uuid        not null,
    label_id       uuid        not null,
    project_id     uuid        null,
    updated_by_id  uuid        null,
    workspace_id   uuid        not null
);

CREATE INDEX draft_issue_labels_created_by_id_88217eef ON draft_issue_labels USING btree (created_by_id);

CREATE INDEX draft_issue_labels_draft_issue_id_339d4c2b ON draft_issue_labels USING btree (draft_issue_id);

CREATE INDEX draft_issue_labels_label_id_b9b001a5 ON draft_issue_labels USING btree (label_id);

CREATE INDEX draft_issue_labels_project_id_16f9ba0a ON draft_issue_labels USING btree (project_id);

CREATE INDEX draft_issue_labels_updated_by_id_edac537c ON draft_issue_labels USING btree (updated_by_id);

CREATE INDEX draft_issue_labels_workspace_id_489a9873 ON draft_issue_labels USING btree (workspace_id);

