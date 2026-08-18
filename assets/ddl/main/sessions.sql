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

-- 最新一条数据示例（latest session_key），已排除生成列，已排除密钥列 session_data, session_key，仅供数据构造参考
-- INSERT INTO "sessions" ("expire_date", "device_info", "user_id") VALUES ('2026-08-10 12:44:48.633891+00:00', '{''domain'': ''http://localhost:3000'', ''ip_address'': ''172.19.0.1'', ''user_agent'': ''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0''}', 'bb96a7c2-ef4b-466f-a2af-92315b642787');
