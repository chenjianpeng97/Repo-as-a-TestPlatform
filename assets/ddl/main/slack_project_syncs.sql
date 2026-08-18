-- auto-generated definition
create table slack_project_syncs
(
    created_at               timestamptz   not null,
    updated_at               timestamptz   not null,
    id                       uuid          not null
        primary key,
    access_token             varchar(300)  not null,
    scopes                   text          not null,
    bot_user_id              varchar(50)   not null,
    webhook_url              varchar(1000) not null,
    data                     jsonb         not null,
    team_id                  varchar(30)   not null,
    team_name                varchar(300)  not null,
    created_by_id            uuid          null,
    project_id               uuid          not null,
    updated_by_id            uuid          null,
    workspace_id             uuid          not null,
    workspace_integration_id uuid          not null,
    deleted_at               timestamptz   null
);

CREATE INDEX slack_project_syncs_created_by_id_ec405a17 ON slack_project_syncs USING btree (created_by_id);

CREATE INDEX slack_project_syncs_project_id_016dc792 ON slack_project_syncs USING btree (project_id);

CREATE INDEX slack_project_syncs_updated_by_id_152eb3b5 ON slack_project_syncs USING btree (updated_by_id);

CREATE INDEX slack_project_syncs_workspace_id_d1822b06 ON slack_project_syncs USING btree (workspace_id);

CREATE INDEX slack_project_syncs_workspace_integration_id_d89c9b40 ON slack_project_syncs USING btree (workspace_integration_id);

CREATE UNIQUE INDEX slack_project_syncs_team_id_project_id_50a144a7_uniq ON slack_project_syncs USING btree (team_id, project_id);

