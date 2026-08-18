-- auto-generated definition
create table pages
(
    created_at           timestamptz      not null,
    updated_at           timestamptz      not null,
    id                   uuid             not null
        primary key,
    name                 text             not null,
    description_json     jsonb            not null,
    description_html     text             not null,
    description_stripped text             null,
    access               smallint         not null,
    created_by_id        uuid             null,
    owned_by_id          uuid             not null,
    updated_by_id        uuid             null,
    workspace_id         uuid             not null,
    color                varchar(255)     not null,
    archived_at          date             null,
    is_locked            boolean          not null,
    parent_id            uuid             null,
    view_props           jsonb            not null,
    logo_props           jsonb            not null,
    description_binary   bytea            null,
    is_global            boolean          not null,
    deleted_at           timestamptz      null,
    moved_to_page        uuid             null,
    moved_to_project     uuid             null,
    external_id          varchar(255)     null,
    external_source      varchar(255)     null,
    sort_order           double precision not null
);

CREATE INDEX pages_created_by_id_d109a675 ON pages USING btree (created_by_id);

CREATE INDEX pages_owned_by_id_bf50485f ON pages USING btree (owned_by_id);

CREATE INDEX pages_parent_id_8b823409 ON pages USING btree (parent_id);

CREATE INDEX pages_updated_by_id_6c42de3e ON pages USING btree (updated_by_id);

CREATE INDEX pages_workspace_id_c6c51010 ON pages USING btree (workspace_id);

