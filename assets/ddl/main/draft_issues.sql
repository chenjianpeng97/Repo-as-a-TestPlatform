-- auto-generated definition
create table draft_issues
(
    created_at           timestamptz      not null,
    updated_at           timestamptz      not null,
    deleted_at           timestamptz      null,
    id                   uuid             not null
        primary key,
    name                 varchar(255)     null,
    description_json     jsonb            not null,
    description_html     text             not null,
    description_stripped text             null,
    description_binary   bytea            null,
    priority             varchar(30)      not null,
    start_date           date             null,
    target_date          date             null,
    sort_order           double precision not null,
    completed_at         timestamptz      null,
    external_source      varchar(255)     null,
    external_id          varchar(255)     null,
    created_by_id        uuid             null,
    estimate_point_id    uuid             null,
    parent_id            uuid             null,
    project_id           uuid             null,
    state_id             uuid             null,
    type_id              uuid             null,
    updated_by_id        uuid             null,
    workspace_id         uuid             not null
);

CREATE INDEX draft_issues_created_by_id_aedba72a ON draft_issues USING btree (created_by_id);

CREATE INDEX draft_issues_estimate_point_id_9e333189 ON draft_issues USING btree (estimate_point_id);

CREATE INDEX draft_issues_parent_id_eee6ec32 ON draft_issues USING btree (parent_id);

CREATE INDEX draft_issues_project_id_784a560c ON draft_issues USING btree (project_id);

CREATE INDEX draft_issues_state_id_94f28f5a ON draft_issues USING btree (state_id);

CREATE INDEX draft_issues_type_id_7a62fe34 ON draft_issues USING btree (type_id);

CREATE INDEX draft_issues_updated_by_id_1ca3cd4e ON draft_issues USING btree (updated_by_id);

CREATE INDEX draft_issues_workspace_id_9d8512c8 ON draft_issues USING btree (workspace_id);

