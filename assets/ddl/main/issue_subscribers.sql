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

