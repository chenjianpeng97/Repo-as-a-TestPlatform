-- auto-generated definition
create table devices
(
    created_at    timestamptz  not null,
    updated_at    timestamptz  not null,
    deleted_at    timestamptz  null,
    id            uuid         not null
        primary key,
    device_id     varchar(255) null,
    device_type   varchar(255) not null,
    push_token    varchar(255) null,
    is_active     boolean      not null,
    created_by_id uuid         null,
    updated_by_id uuid         null,
    user_id       uuid         not null
);

CREATE INDEX devices_created_by_id_410a755b ON devices USING btree (created_by_id);

CREATE INDEX devices_updated_by_id_ee20dc3c ON devices USING btree (updated_by_id);

CREATE INDEX devices_user_id_9a5cca49 ON devices USING btree (user_id);

