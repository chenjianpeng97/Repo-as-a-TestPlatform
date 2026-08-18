-- auto-generated definition
create table device_sessions
(
    created_at    timestamptz  not null,
    updated_at    timestamptz  not null,
    deleted_at    timestamptz  null,
    id            uuid         not null
        primary key,
    is_active     boolean      not null,
    user_agent    varchar(255) null,
    ip_address    inet         null,
    start_time    timestamptz  not null,
    end_time      timestamptz  null,
    created_by_id uuid         null,
    device_id     uuid         not null,
    session_id    varchar(128) not null,
    updated_by_id uuid         null
);

CREATE INDEX device_sessions_created_by_id_920a3bd5 ON device_sessions USING btree (created_by_id);

CREATE INDEX device_sessions_device_id_a42b2ada ON device_sessions USING btree (device_id);

CREATE INDEX device_sessions_session_id_5382b02b ON device_sessions USING btree (session_id);

CREATE INDEX device_sessions_session_id_5382b02b_like ON device_sessions USING btree (session_id varchar_pattern_ops);

CREATE INDEX device_sessions_updated_by_id_d0bd0c76 ON device_sessions USING btree (updated_by_id);

