-- auto-generated definition
create table debug_toolbar_historyentry
(
    request_id uuid        not null
        primary key,
    data       jsonb       not null,
    created_at timestamptz not null
);

-- （debug_toolbar_historyentry 暂无数据，无示例 INSERT）
