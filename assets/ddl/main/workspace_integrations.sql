-- auto-generated definition
create table workspace_integrations
(
    created_at     timestamptz not null,
    updated_at     timestamptz not null,
    id             uuid        not null
        primary key,
    metadata       jsonb       not null,
    config         jsonb       not null,
    actor_id       uuid        not null,
    api_token_id   uuid        not null,
    created_by_id  uuid        null,
    integration_id uuid        not null,
    updated_by_id  uuid        null,
    workspace_id   uuid        not null,
    deleted_at     timestamptz null
);

CREATE INDEX workspace_integrations_actor_id_21619aa1 ON workspace_integrations USING btree (actor_id);

CREATE INDEX workspace_integrations_api_token_id_bdb1759b ON workspace_integrations USING btree (api_token_id);

CREATE INDEX workspace_integrations_created_by_id_37639c73 ON workspace_integrations USING btree (created_by_id);

CREATE INDEX workspace_integrations_integration_id_6cb0aace ON workspace_integrations USING btree (integration_id);

CREATE INDEX workspace_integrations_updated_by_id_fce01dcb ON workspace_integrations USING btree (updated_by_id);

CREATE INDEX workspace_integrations_workspace_id_27ebeb6b ON workspace_integrations USING btree (workspace_id);

CREATE UNIQUE INDEX workspace_integrations_workspace_id_integration_fa041c22_uniq ON workspace_integrations USING btree (workspace_id, integration_id);

