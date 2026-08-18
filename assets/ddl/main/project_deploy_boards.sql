-- auto-generated definition
create table project_deploy_boards
(
    created_at    timestamptz  not null,
    updated_at    timestamptz  not null,
    id            uuid         not null
        primary key,
    anchor        varchar(255) not null,
    comments      boolean      not null,
    reactions     boolean      not null,
    votes         boolean      not null,
    views         jsonb        not null,
    created_by_id uuid         null,
    intake_id     uuid         null,
    project_id    uuid         not null,
    updated_by_id uuid         null,
    workspace_id  uuid         not null,
    deleted_at    timestamptz  null
);

CREATE INDEX project_deploy_boards_anchor_b61b8817_like ON project_deploy_boards USING btree (anchor varchar_pattern_ops);

CREATE INDEX project_deploy_boards_created_by_id_2ea72f98 ON project_deploy_boards USING btree (created_by_id);

CREATE INDEX project_deploy_boards_inbox_id_a6a75525 ON project_deploy_boards USING btree (intake_id);

CREATE INDEX project_deploy_boards_project_id_49d887b2 ON project_deploy_boards USING btree (project_id);

CREATE INDEX project_deploy_boards_updated_by_id_290eb99e ON project_deploy_boards USING btree (updated_by_id);

CREATE INDEX project_deploy_boards_workspace_id_cd92f164 ON project_deploy_boards USING btree (workspace_id);

CREATE UNIQUE INDEX project_deploy_boards_anchor_key ON project_deploy_boards USING btree (anchor);

CREATE UNIQUE INDEX project_deploy_boards_project_id_anchor_893d365a_uniq ON project_deploy_boards USING btree (project_id, anchor);

