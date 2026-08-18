-- auto-generated definition
create table issue_relations
(
    created_at       timestamptz not null,
    updated_at       timestamptz not null,
    id               uuid        not null
        primary key,
    relation_type    varchar(20) not null,
    created_by_id    uuid        null,
    issue_id         uuid        not null,
    project_id       uuid        not null,
    related_issue_id uuid        not null,
    updated_by_id    uuid        null,
    workspace_id     uuid        not null,
    deleted_at       timestamptz null
);

CREATE INDEX issue_relations_created_by_id_854d07e7 ON issue_relations USING btree (created_by_id);

CREATE INDEX issue_relations_issue_id_e1db6f72 ON issue_relations USING btree (issue_id);

CREATE INDEX issue_relations_project_id_15350161 ON issue_relations USING btree (project_id);

CREATE INDEX issue_relations_related_issue_id_e1ea44a7 ON issue_relations USING btree (related_issue_id);

CREATE INDEX issue_relations_updated_by_id_3dfa850f ON issue_relations USING btree (updated_by_id);

CREATE INDEX issue_relations_workspace_id_00b50e90 ON issue_relations USING btree (workspace_id);

CREATE UNIQUE INDEX issue_relation_unique_issue_related_issue_when_deleted_at_null ON issue_relations USING btree (issue_id, related_issue_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX issue_relations_issue_id_related_issue_i_cc724584_uniq ON issue_relations USING btree (issue_id, related_issue_id, deleted_at);

