-- auto-generated definition
create table notifications
(
    created_at        timestamptz  not null,
    updated_at        timestamptz  not null,
    id                uuid         not null
        primary key,
    data              jsonb        null,
    entity_identifier uuid         null,
    entity_name       varchar(255) not null,
    title             text         not null,
    message           jsonb        null,
    message_html      text         not null,
    message_stripped  text         null,
    sender            varchar(255) not null,
    read_at           timestamptz  null,
    snoozed_till      timestamptz  null,
    archived_at       timestamptz  null,
    created_by_id     uuid         null,
    project_id        uuid         null,
    receiver_id       uuid         not null,
    triggered_by_id   uuid         null,
    updated_by_id     uuid         null,
    workspace_id      uuid         not null,
    deleted_at        timestamptz  null
);

CREATE INDEX notif_entity_identifier_idx ON notifications USING btree (entity_identifier);

CREATE INDEX notif_entity_idx ON notifications USING btree (receiver_id, read_at);

CREATE INDEX notif_entity_lookup_idx ON notifications USING btree (workspace_id, entity_identifier, entity_name);

CREATE INDEX notif_entity_name_idx ON notifications USING btree (entity_name);

CREATE INDEX notif_read_at_idx ON notifications USING btree (read_at);

CREATE INDEX notif_receiver_entity_idx ON notifications USING btree (receiver_id, workspace_id, entity_name, read_at);

CREATE INDEX notif_receiver_sender_idx ON notifications USING btree (receiver_id, workspace_id, sender);

CREATE INDEX notif_receiver_state_idx ON notifications USING btree (receiver_id, workspace_id, snoozed_till, archived_at);

CREATE INDEX notif_receiver_status_idx ON notifications USING btree (receiver_id, workspace_id, read_at, created_at);

CREATE INDEX notifications_created_by_id_b9c3f81b ON notifications USING btree (created_by_id);

CREATE INDEX notifications_project_id_e4d4f192 ON notifications USING btree (project_id);

CREATE INDEX notifications_receiver_id_b708b2b0 ON notifications USING btree (receiver_id);

CREATE INDEX notifications_triggered_by_id_31cdec21 ON notifications USING btree (triggered_by_id);

CREATE INDEX notifications_updated_by_id_8a651e96 ON notifications USING btree (updated_by_id);

CREATE INDEX notifications_workspace_id_b2f09ef7 ON notifications USING btree (workspace_id);

-- （notifications 暂无数据，无示例 INSERT）
