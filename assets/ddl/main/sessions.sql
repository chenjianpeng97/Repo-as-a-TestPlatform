-- auto-generated definition
create table sessions
(
    session_data text         not null,
    expire_date  timestamptz  not null,
    device_info  jsonb        null,
    session_key  varchar(128) not null
        primary key,
    user_id      varchar(50)  null
);

CREATE INDEX sessions_expire_date_16e4c444 ON sessions USING btree (expire_date);

CREATE INDEX sessions_session_key_58f9471b_like ON sessions USING btree (session_key varchar_pattern_ops);

CREATE INDEX sessions_user_id_05e26f4a ON sessions USING btree (user_id);

CREATE INDEX sessions_user_id_05e26f4a_like ON sessions USING btree (user_id varchar_pattern_ops);

