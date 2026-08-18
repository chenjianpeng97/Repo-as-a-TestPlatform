-- auto-generated definition
create table issue_attachments
(
    created_at      timestamptz  not null,
    updated_at      timestamptz  not null,
    id              uuid         not null
        primary key,
    attributes      jsonb        not null,
    asset           varchar(100) not null,
    created_by_id   uuid         null,
    issue_id        uuid         not null,
    project_id      uuid         not null,
    updated_by_id   uuid         null,
    workspace_id    uuid         not null,
    external_id     varchar(255) null,
    external_source varchar(255) null,
    deleted_at      timestamptz  null
);

CREATE INDEX issue_attachments_created_by_id_87be05bb ON issue_attachments USING btree (created_by_id);

CREATE INDEX issue_attachments_issue_id_0faf88bf ON issue_attachments USING btree (issue_id);

CREATE INDEX issue_attachments_project_id_a95fe706 ON issue_attachments USING btree (project_id);

CREATE INDEX issue_attachments_updated_by_id_47dceec1 ON issue_attachments USING btree (updated_by_id);

CREATE INDEX issue_attachments_workspace_id_c456a532 ON issue_attachments USING btree (workspace_id);

-- （issue_attachments 暂无数据，无示例 INSERT）
