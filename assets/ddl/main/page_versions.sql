-- auto-generated definition
create table page_versions
(
    created_at           timestamptz not null,
    updated_at           timestamptz not null,
    id                   uuid        not null
        primary key,
    last_saved_at        timestamptz not null,
    description_binary   bytea       null,
    description_html     text        not null,
    description_stripped text        null,
    description_json     jsonb       not null,
    created_by_id        uuid        null,
    owned_by_id          uuid        not null,
    page_id              uuid        not null,
    updated_by_id        uuid        null,
    workspace_id         uuid        not null,
    deleted_at           timestamptz null,
    sub_pages_data       jsonb       not null
);

CREATE INDEX page_versions_created_by_id_d660b13b ON page_versions USING btree (created_by_id);

CREATE INDEX page_versions_owned_by_id_6d9143db ON page_versions USING btree (owned_by_id);

CREATE INDEX page_versions_page_id_c46471da ON page_versions USING btree (page_id);

CREATE INDEX page_versions_updated_by_id_72d5e579 ON page_versions USING btree (updated_by_id);

CREATE INDEX page_versions_workspace_id_8330a200 ON page_versions USING btree (workspace_id);

-- （page_versions 暂无数据，无示例 INSERT）
