-- auto-generated definition
create table cycle_issues
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    id            uuid        not null
        primary key,
    created_by_id uuid        null,
    cycle_id      uuid        not null,
    issue_id      uuid        not null,
    project_id    uuid        not null,
    updated_by_id uuid        null,
    workspace_id  uuid        not null,
    deleted_at    timestamptz null
);

CREATE INDEX cycle_issue_created_by_id_30b27539 ON cycle_issues USING btree (created_by_id);

CREATE INDEX cycle_issue_cycle_id_ec681215 ON cycle_issues USING btree (cycle_id);

CREATE INDEX cycle_issue_project_id_6ad3257a ON cycle_issues USING btree (project_id);

CREATE INDEX cycle_issue_updated_by_id_cb4516f2 ON cycle_issues USING btree (updated_by_id);

CREATE INDEX cycle_issue_workspace_id_1d77330e ON cycle_issues USING btree (workspace_id);

CREATE INDEX cycle_issues_issue_id_2d5ac97f ON cycle_issues USING btree (issue_id);

CREATE UNIQUE INDEX cycle_issue_when_deleted_at_null ON cycle_issues USING btree (cycle_id, issue_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX cycle_issues_issue_id_cycle_id_deleted_at_93e8fecd_uniq ON cycle_issues USING btree (issue_id, cycle_id, deleted_at);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "cycle_issues" ("created_at", "updated_at", "id", "created_by_id", "cycle_id", "issue_id", "project_id", "updated_by_id", "workspace_id", "deleted_at") VALUES ('2026-07-10 12:37:56.446713+00:00', '2026-07-10 12:37:56.446731+00:00', 'c93ab442-3ff6-495d-88b6-e7b635d260b8', NULL, '2b651f63-062f-4632-83cf-267dee34a667', '3505a9d6-ff51-43bb-b419-82e9bfb13bd4', 'dc06dab7-13f5-40de-9d63-79d71315d44b', NULL, '6f2f3ff8-62de-4127-978b-54991c166df3', NULL);
