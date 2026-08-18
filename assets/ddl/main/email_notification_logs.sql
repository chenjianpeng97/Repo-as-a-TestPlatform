-- auto-generated definition
create table email_notification_logs
(
    created_at        timestamptz  not null,
    updated_at        timestamptz  not null,
    id                uuid         not null
        primary key,
    entity_identifier uuid         null,
    entity_name       varchar(255) not null,
    data              jsonb        null,
    processed_at      timestamptz  null,
    sent_at           timestamptz  null,
    entity            varchar(200) not null,
    old_value         varchar(300) null,
    new_value         varchar(300) null,
    created_by_id     uuid         null,
    receiver_id       uuid         not null,
    triggered_by_id   uuid         not null,
    updated_by_id     uuid         null,
    deleted_at        timestamptz  null
);

CREATE INDEX email_notification_logs_created_by_id_6faff587 ON email_notification_logs USING btree (created_by_id);

CREATE INDEX email_notification_logs_receiver_id_7c7d2e13 ON email_notification_logs USING btree (receiver_id);

CREATE INDEX email_notification_logs_triggered_by_id_b551e727 ON email_notification_logs USING btree (triggered_by_id);

CREATE INDEX email_notification_logs_updated_by_id_5d99c798 ON email_notification_logs USING btree (updated_by_id);

