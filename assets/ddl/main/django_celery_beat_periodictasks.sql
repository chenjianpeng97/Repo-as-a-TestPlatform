-- auto-generated definition
create table django_celery_beat_periodictasks
(
    ident       smallint    not null
        primary key,
    last_update timestamptz not null
);

-- 最新一条数据示例（latest ident），已排除生成列，仅供数据构造参考
-- INSERT INTO "django_celery_beat_periodictasks" ("ident", "last_update") VALUES (1, '2026-08-17 02:37:23.767453+00:00');
