-- auto-generated definition
create table issue_labels
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    id            uuid        not null
        primary key,
    created_by_id uuid        null,
    issue_id      uuid        not null,
    label_id      uuid        not null,
    project_id    uuid        not null,
    updated_by_id uuid        null,
    workspace_id  uuid        not null,
    deleted_at    timestamptz null
);

CREATE INDEX issue_label_created_by_id_94075315 ON issue_labels USING btree (created_by_id);

CREATE INDEX issue_label_issue_id_0f252e52 ON issue_labels USING btree (issue_id);

CREATE INDEX issue_label_label_id_5f22777f ON issue_labels USING btree (label_id);

CREATE INDEX issue_label_project_id_eaa2ba39 ON issue_labels USING btree (project_id);

CREATE INDEX issue_label_updated_by_id_a97a6733 ON issue_labels USING btree (updated_by_id);

CREATE INDEX issue_label_workspace_id_b5b1faac ON issue_labels USING btree (workspace_id);

