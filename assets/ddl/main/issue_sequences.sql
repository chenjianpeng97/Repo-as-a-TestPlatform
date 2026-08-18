-- auto-generated definition
create table issue_sequences
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    id            uuid        not null
        primary key,
    sequence      bigint      not null,
    deleted       boolean     not null,
    created_by_id uuid        null,
    issue_id      uuid        null,
    project_id    uuid        not null,
    updated_by_id uuid        null,
    workspace_id  uuid        not null,
    deleted_at    timestamptz null
);

CREATE INDEX issue_sequence_created_by_id_59270506 ON issue_sequences USING btree (created_by_id);

CREATE INDEX issue_sequence_issue_id_16e9f00f ON issue_sequences USING btree (issue_id);

CREATE INDEX issue_sequence_project_id_ce882e85 ON issue_sequences USING btree (project_id);

CREATE INDEX issue_sequence_updated_by_id_310c8dd3 ON issue_sequences USING btree (updated_by_id);

CREATE INDEX issue_sequence_workspace_id_0d3f0fd4 ON issue_sequences USING btree (workspace_id);

CREATE INDEX issue_sequences_sequence_2c9458d4 ON issue_sequences USING btree (sequence);

