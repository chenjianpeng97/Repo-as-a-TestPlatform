-- auto-generated definition
create table user_recent_visits
(
    created_at        timestamptz not null,
    updated_at        timestamptz not null,
    id                uuid        not null
        primary key,
    entity_identifier uuid        null,
    entity_name       varchar(30) not null,
    visited_at        timestamptz not null,
    created_by_id     uuid        null,
    project_id        uuid        null,
    updated_by_id     uuid        null,
    user_id           uuid        not null,
    workspace_id      uuid        not null,
    deleted_at        timestamptz null
);

CREATE INDEX user_recent_visits_created_by_id_a655b75f ON user_recent_visits USING btree (created_by_id);

CREATE INDEX user_recent_visits_project_id_e5eecf27 ON user_recent_visits USING btree (project_id);

CREATE INDEX user_recent_visits_updated_by_id_42b12ef2 ON user_recent_visits USING btree (updated_by_id);

CREATE INDEX user_recent_visits_user_id_f5153288 ON user_recent_visits USING btree (user_id);

CREATE INDEX user_recent_visits_workspace_id_362a4e80 ON user_recent_visits USING btree (workspace_id);

