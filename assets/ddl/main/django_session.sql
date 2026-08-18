-- auto-generated definition
create table django_session
(
    session_key  varchar(40) not null
        primary key,
    session_data text        not null,
    expire_date  timestamptz not null
);

CREATE INDEX django_session_expire_date_a5c62663 ON django_session USING btree (expire_date);

CREATE INDEX django_session_session_key_c0390e0f_like ON django_session USING btree (session_key varchar_pattern_ops);

-- （django_session 暂无数据，无示例 INSERT）
