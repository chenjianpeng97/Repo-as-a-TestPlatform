-- auto-generated definition
create table profiles
(
    created_at                   timestamptz  not null,
    updated_at                   timestamptz  not null,
    id                           uuid         not null
        primary key,
    theme                        jsonb        not null,
    is_tour_completed            boolean      not null,
    onboarding_step              jsonb        not null,
    use_case                     text         null,
    role                         varchar(300) null,
    is_onboarded                 boolean      not null,
    last_workspace_id            uuid         null,
    billing_address_country      varchar(255) not null,
    billing_address              jsonb        null,
    has_billing_address          boolean      not null,
    company_name                 varchar(255) not null,
    user_id                      uuid         not null,
    is_mobile_onboarded          boolean      not null,
    mobile_onboarding_step       jsonb        not null,
    mobile_timezone_auto_set     boolean      not null,
    language                     varchar(255) not null,
    is_smooth_cursor_enabled     boolean      not null,
    start_of_the_week            smallint     not null,
    is_app_rail_docked           boolean      not null,
    background_color             varchar(255) not null,
    goals                        jsonb        not null,
    has_marketing_email_consent  boolean      not null,
    is_navigation_tour_completed boolean      not null,
    is_subscribed_to_changelog   boolean      not null,
    notification_view_mode       varchar(255) not null,
    product_tour                 jsonb        not null
);

CREATE UNIQUE INDEX profiles_user_id_key ON profiles USING btree (user_id);

