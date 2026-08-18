-- auto-generated definition
create table issue_versions
(
    created_at      timestamptz      not null,
    updated_at      timestamptz      not null,
    deleted_at      timestamptz      null,
    id              uuid             not null
        primary key,
    parent          uuid             null,
    state           uuid             null,
    estimate_point  uuid             null,
    name            varchar(255)     not null,
    priority        varchar(30)      not null,
    start_date      date             null,
    target_date     date             null,
    sequence_id     integer          not null,
    sort_order      double precision not null,
    completed_at    timestamptz      null,
    archived_at     date             null,
    is_draft        boolean          not null,
    external_source varchar(255)     null,
    external_id     varchar(255)     null,
    type            uuid             null,
    last_saved_at   timestamptz      not null,
    owned_by_id     uuid             not null,
    assignees       uuid[]           not null,
    labels          uuid[]           not null,
    cycle           uuid             null,
    modules         uuid[]           not null,
    properties      jsonb            not null,
    meta            jsonb            not null,
    created_by_id   uuid             null,
    issue_id        uuid             not null,
    project_id      uuid             not null,
    updated_by_id   uuid             null,
    workspace_id    uuid             not null,
    activity_id     uuid             null
);

CREATE INDEX issue_versions_activity_id_b1872ffc ON issue_versions USING btree (activity_id);

CREATE INDEX issue_versions_created_by_id_a782830a ON issue_versions USING btree (created_by_id);

CREATE INDEX issue_versions_issue_id_25cf001c ON issue_versions USING btree (issue_id);

CREATE INDEX issue_versions_owned_by_id_7586378d ON issue_versions USING btree (owned_by_id);

CREATE INDEX issue_versions_project_id_a069ad03 ON issue_versions USING btree (project_id);

CREATE INDEX issue_versions_updated_by_id_dcae6dd2 ON issue_versions USING btree (updated_by_id);

CREATE INDEX issue_versions_workspace_id_b8c48b7c ON issue_versions USING btree (workspace_id);

-- （issue_versions 暂无数据，无示例 INSERT）
