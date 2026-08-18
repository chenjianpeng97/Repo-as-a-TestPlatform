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

