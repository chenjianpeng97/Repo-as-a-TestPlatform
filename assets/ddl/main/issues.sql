-- auto-generated definition
create table issues
(
    created_at           timestamptz      not null,
    updated_at           timestamptz      not null,
    id                   uuid             not null
        primary key,
    name                 varchar(255)     not null,
    description_json     jsonb            not null,
    priority             varchar(30)      not null,
    start_date           date             null,
    target_date          date             null,
    sequence_id          integer          not null,
    created_by_id        uuid             null,
    parent_id            uuid             null,
    project_id           uuid             not null,
    state_id             uuid             null,
    updated_by_id        uuid             null,
    workspace_id         uuid             not null,
    description_html     text             not null,
    description_stripped text             null,
    completed_at         timestamptz      null,
    sort_order           double precision not null,
    point                integer          null,
    archived_at          date             null,
    is_draft             boolean          not null,
    external_id          varchar(255)     null,
    external_source      varchar(255)     null,
    description_binary   bytea            null,
    estimate_point_id    uuid             null,
    type_id              uuid             null,
    deleted_at           timestamptz      null
);

CREATE INDEX issue_created_by_id_8f0ae62b ON issues USING btree (created_by_id);

CREATE INDEX issue_parent_id_ce8d76ba ON issues USING btree (parent_id);

CREATE INDEX issue_project_id_fea0fc80 ON issues USING btree (project_id);

CREATE INDEX issue_state_id_1a65560d ON issues USING btree (state_id);

CREATE INDEX issue_updated_by_id_f1261863 ON issues USING btree (updated_by_id);

CREATE INDEX issue_workspace_id_c84878c1 ON issues USING btree (workspace_id);

CREATE INDEX issues_estimate_point_id_a6822abe ON issues USING btree (estimate_point_id);

CREATE INDEX issues_type_id_a4710b19 ON issues USING btree (type_id);

