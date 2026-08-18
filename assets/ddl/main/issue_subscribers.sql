-- auto-generated definition
create table issue_subscribers
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    id            uuid        not null
        primary key,
    created_by_id uuid        null,
    issue_id      uuid        not null,
    project_id    uuid        not null,
    subscriber_id uuid        not null,
    updated_by_id uuid        null,
    workspace_id  uuid        not null,
    deleted_at    timestamptz null
);

CREATE INDEX issue_subscribers_created_by_id_b6ea0157 ON issue_subscribers USING btree (created_by_id);

CREATE INDEX issue_subscribers_issue_id_85cf2093 ON issue_subscribers USING btree (issue_id);

CREATE INDEX issue_subscribers_project_id_cf48d75f ON issue_subscribers USING btree (project_id);

CREATE INDEX issue_subscribers_subscriber_id_2d89c988 ON issue_subscribers USING btree (subscriber_id);

CREATE INDEX issue_subscribers_updated_by_id_1bfc2f55 ON issue_subscribers USING btree (updated_by_id);

CREATE INDEX issue_subscribers_workspace_id_96afa91f ON issue_subscribers USING btree (workspace_id);

CREATE UNIQUE INDEX issue_subscriber_unique_issue_subscriber_when_deleted_at_null ON issue_subscribers USING btree (issue_id, subscriber_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX issue_subscribers_issue_id_subscriber_id_d_587dec1a_uniq ON issue_subscribers USING btree (issue_id, subscriber_id, deleted_at);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "issue_subscribers" ("created_at", "updated_at", "id", "created_by_id", "issue_id", "project_id", "subscriber_id", "updated_by_id", "workspace_id", "deleted_at") VALUES ('2026-07-14 09:40:16.324693+00:00', '2026-07-14 09:40:16.324717+00:00', 'b6871a47-c66d-476b-89be-f227c59f50d8', NULL, 'fd913c95-c2e4-49b0-b0ef-b68d06b55342', 'ec840712-e7ae-41f7-bc45-ff324bee0248', '9d1f264d-7dee-48c5-ab98-087db907b8a1', NULL, '6f2f3ff8-62de-4127-978b-54991c166df3', NULL);
