-- auto-generated definition
create table stickies
(
    created_at           timestamptz      not null,
    updated_at           timestamptz      not null,
    deleted_at           timestamptz      null,
    id                   uuid             not null
        primary key,
    name                 text             null,
    description          jsonb            not null,
    description_html     text             not null,
    description_stripped text             null,
    description_binary   bytea            null,
    logo_props           jsonb            not null,
    color                varchar(255)     null,
    background_color     varchar(255)     null,
    created_by_id        uuid             null,
    owner_id             uuid             not null,
    updated_by_id        uuid             null,
    workspace_id         uuid             not null,
    sort_order           double precision not null
);

CREATE INDEX stickies_created_by_id_f72e05c4 ON stickies USING btree (created_by_id);

CREATE INDEX stickies_owner_id_6ee3be2b ON stickies USING btree (owner_id);

CREATE INDEX stickies_updated_by_id_d660f1fb ON stickies USING btree (updated_by_id);

CREATE INDEX stickies_workspace_id_0094496a ON stickies USING btree (workspace_id);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "stickies" ("created_at", "updated_at", "deleted_at", "id", "name", "description", "description_html", "description_stripped", "description_binary", "logo_props", "color", "background_color", "created_by_id", "owner_id", "updated_by_id", "workspace_id", "sort_order") VALUES ('2026-07-14 08:56:33.476913+00:00', '2026-07-14 08:56:41.729280+00:00', NULL, '987e40c5-62b6-4f21-927d-8339ee047303', NULL, '{}', '<p class="editor-paragraph-block" data-id="dd632c9f-b79c-4c9f-8d86-4f55bca4a800">rule 1</p>', 'rule 1', NULL, '{}', NULL, 'dark-blue', '9d1f264d-7dee-48c5-ab98-087db907b8a1', '9d1f264d-7dee-48c5-ab98-087db907b8a1', '9d1f264d-7dee-48c5-ab98-087db907b8a1', '6f2f3ff8-62de-4127-978b-54991c166df3', 75535.0);
