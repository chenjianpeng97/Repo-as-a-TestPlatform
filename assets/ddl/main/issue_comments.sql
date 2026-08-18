-- auto-generated definition
create table issue_comments
(
    created_at       timestamptz    not null,
    updated_at       timestamptz    not null,
    id               uuid           not null
        primary key,
    comment_stripped text           not null,
    attachments      varchar(200)[] not null,
    created_by_id    uuid           null,
    issue_id         uuid           not null,
    project_id       uuid           not null,
    updated_by_id    uuid           null,
    workspace_id     uuid           not null,
    actor_id         uuid           null,
    comment_html     text           not null,
    comment_json     jsonb          not null,
    access           varchar(100)   not null,
    external_id      varchar(255)   null,
    external_source  varchar(255)   null,
    deleted_at       timestamptz    null,
    edited_at        timestamptz    null,
    description_id   uuid           null,
    parent_id        uuid           null
);

CREATE INDEX issue_comment_actor_id_d312315b ON issue_comments USING btree (actor_id);

CREATE INDEX issue_comment_created_by_id_0765f239 ON issue_comments USING btree (created_by_id);

CREATE INDEX issue_comment_issue_id_d0195e35 ON issue_comments USING btree (issue_id);

CREATE INDEX issue_comment_project_id_db37c105 ON issue_comments USING btree (project_id);

CREATE INDEX issue_comment_updated_by_id_96cfb86e ON issue_comments USING btree (updated_by_id);

CREATE INDEX issue_comment_workspace_id_3f7969ec ON issue_comments USING btree (workspace_id);

CREATE INDEX issue_comments_parent_id_d8db10b1 ON issue_comments USING btree (parent_id);

CREATE UNIQUE INDEX issue_comments_description_id_key ON issue_comments USING btree (description_id);

