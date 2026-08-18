-- auto-generated definition
create table issue_reactions
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    id            uuid        not null
        primary key,
    reaction      text        not null,
    actor_id      uuid        not null,
    created_by_id uuid        null,
    issue_id      uuid        not null,
    project_id    uuid        not null,
    updated_by_id uuid        null,
    workspace_id  uuid        not null,
    deleted_at    timestamptz null
);

CREATE INDEX issue_reactions_actor_id_5f5b8303 ON issue_reactions USING btree (actor_id);

CREATE INDEX issue_reactions_created_by_id_3953b7de ON issue_reactions USING btree (created_by_id);

CREATE INDEX issue_reactions_issue_id_2c324bae ON issue_reactions USING btree (issue_id);

CREATE INDEX issue_reactions_project_id_8708ecaf ON issue_reactions USING btree (project_id);

CREATE INDEX issue_reactions_updated_by_id_4069af90 ON issue_reactions USING btree (updated_by_id);

CREATE INDEX issue_reactions_workspace_id_bd8d7550 ON issue_reactions USING btree (workspace_id);

CREATE UNIQUE INDEX issue_reaction_unique_issue_actor_reaction_when_deleted_at_null ON issue_reactions USING btree (issue_id, actor_id, reaction) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX issue_reactions_issue_id_actor_id_reacti_7da73ced_uniq ON issue_reactions USING btree (issue_id, actor_id, reaction, deleted_at);

