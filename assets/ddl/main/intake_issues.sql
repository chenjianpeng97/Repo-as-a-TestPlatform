-- auto-generated definition
create table intake_issues
(
    created_at      timestamptz  not null,
    updated_at      timestamptz  not null,
    id              uuid         not null
        primary key,
    status          integer      not null,
    snoozed_till    timestamptz  null,
    source          varchar(255) null,
    created_by_id   uuid         null,
    duplicate_to_id uuid         null,
    intake_id       uuid         not null,
    issue_id        uuid         not null,
    project_id      uuid         not null,
    updated_by_id   uuid         null,
    workspace_id    uuid         not null,
    external_id     varchar(255) null,
    external_source varchar(255) null,
    deleted_at      timestamptz  null,
    extra           jsonb        not null,
    source_email    text         null
);

CREATE INDEX inbox_issues_created_by_id_483bce13 ON intake_issues USING btree (created_by_id);

CREATE INDEX inbox_issues_duplicate_to_id_6cb8d961 ON intake_issues USING btree (duplicate_to_id);

CREATE INDEX inbox_issues_inbox_id_444b05b9 ON intake_issues USING btree (intake_id);

CREATE INDEX inbox_issues_issue_id_7d74b224 ON intake_issues USING btree (issue_id);

CREATE INDEX inbox_issues_project_id_5117a70b ON intake_issues USING btree (project_id);

CREATE INDEX inbox_issues_updated_by_id_d1b2b70f ON intake_issues USING btree (updated_by_id);

CREATE INDEX inbox_issues_workspace_id_4a61a7bd ON intake_issues USING btree (workspace_id);

