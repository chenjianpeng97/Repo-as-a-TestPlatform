-- auto-generated definition
create table issue_activities
(
    created_at       timestamptz      not null,
    updated_at       timestamptz      not null,
    id               uuid             not null
        primary key,
    verb             varchar(255)     not null,
    field            varchar(255)     null,
    old_value        text             null,
    new_value        text             null,
    comment          text             not null,
    attachments      varchar(200)[]   not null,
    created_by_id    uuid             null,
    issue_id         uuid             null,
    issue_comment_id uuid             null,
    project_id       uuid             not null,
    updated_by_id    uuid             null,
    workspace_id     uuid             not null,
    actor_id         uuid             null,
    new_identifier   uuid             null,
    old_identifier   uuid             null,
    epoch            double precision null,
    deleted_at       timestamptz      null
);

CREATE INDEX issue_activity_actor_id_52fdd42d ON issue_activities USING btree (actor_id);

CREATE INDEX issue_activity_created_by_id_49516e3d ON issue_activities USING btree (created_by_id);

CREATE INDEX issue_activity_issue_comment_id_701f3c3c ON issue_activities USING btree (issue_comment_id);

CREATE INDEX issue_activity_issue_id_807fbde4 ON issue_activities USING btree (issue_id);

CREATE INDEX issue_activity_project_id_d0ac2ccf ON issue_activities USING btree (project_id);

CREATE INDEX issue_activity_updated_by_id_0075f9bd ON issue_activities USING btree (updated_by_id);

CREATE INDEX issue_activity_workspace_id_65acaf73 ON issue_activities USING btree (workspace_id);

