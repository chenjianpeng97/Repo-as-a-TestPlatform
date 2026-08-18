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

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "issue_activities" ("created_at", "updated_at", "id", "verb", "field", "old_value", "new_value", "comment", "attachments", "created_by_id", "issue_id", "issue_comment_id", "project_id", "updated_by_id", "workspace_id", "actor_id", "new_identifier", "old_identifier", "epoch", "deleted_at") VALUES ('2026-07-10 12:37:56.420226+00:00', '2026-07-10 12:37:56.420232+00:00', 'fe069738-0faf-4d5d-935b-bbf2309b2c07', 'created', NULL, NULL, NULL, 'created the issue', '[]', NULL, '75270633-9c1b-4931-a6ed-cf2c6c80da2c', NULL, 'dc06dab7-13f5-40de-9d63-79d71315d44b', NULL, '6f2f3ff8-62de-4127-978b-54991c166df3', '7f979bbb-cc06-4739-a6bb-0348e80efda7', NULL, NULL, 1783687076.4189389, NULL);
