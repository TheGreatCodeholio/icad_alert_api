-- create table users
CREATE TABLE IF NOT EXISTS `users`
(
    `user_id`       int(11) AUTO_INCREMENT PRIMARY KEY,
    `user_email`    VARCHAR(255) DEFAULT NULL,
    `user_username` VARCHAR(255) NOT NULL,
    `user_password` VARCHAR(255) NOT NULL
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci;

-- create user security table --
CREATE TABLE IF NOT EXISTS `user_security`
(
    `user_security_id`      int(11) AUTO_INCREMENT PRIMARY KEY,
    `user_id`               int(11)    NOT NULL,
    `is_active`             tinyint(4) NOT NULL DEFAULT 1,
    `last_login_date`       bigint(20) NOT NULL,
    `failed_login_attempts` int(11)    NOT NULL DEFAULT 0,
    `account_locked_until`  bigint(20) NOT NULL DEFAULT 0,
    FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci;

-- create radio system table
CREATE TABLE IF NOT EXISTS `radio_systems`
(
    `system_id`         int(11) AUTO_INCREMENT PRIMARY KEY,
    `system_short_name` varchar(255) DEFAULT NULL,
    `system_name`       varchar(255) DEFAULT NULL,
    `system_county`     varchar(255) DEFAULT NULL,
    `system_state`      varchar(255) DEFAULT NULL,
    `system_fips`       int(11)      DEFAULT NULL,
    `system_api_key`    varchar(64)  DEFAULT NULL,
    `stream_url`        varchar(255) DEFAULT NULL
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `radio_system_email_settings`
(
    `email_setting_id`    int(11) AUTO_INCREMENT PRIMARY KEY,
    `system_id`           int(11),
    `email_enabled`       tinyint(1) NOT NULL DEFAULT 0,
    `smtp_hostname`       varchar(255)        DEFAULT NULL,
    `smtp_port`           int(11)             DEFAULT NULL,
    `smtp_username`       varchar(255)        DEFAULT NULL,
    `smtp_password`       varchar(255)        DEFAULT NULL,
    `smtp_security`       tinyint(1)          DEFAULT 2,
    `email_address_from`  varchar(255)        DEFAULT 'dispatch@example.com',
    `email_text_from`     varchar(255)        DEFAULT 'iCAD Dispatch',
    `email_alert_subject` varchar(512)        DEFAULT 'Dispatch Alert',
    `email_alert_body`    text,
    FOREIGN KEY (`system_id`) REFERENCES `radio_systems` (`system_id`) ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `radio_system_pushover_settings`
(
    `pushover_setting_id`  int(11) AUTO_INCREMENT PRIMARY KEY,
    `system_id`            int(11),
    `pushover_enabled`     tinyint(1) NOT NULL DEFAULT 0,
    `pushover_group_token` varchar(255)        DEFAULT NULL,
    `pushover_app_token`   varchar(255)        DEFAULT NULL,
    `pushover_body`        text,
    `pushover_subject`     varchar(255)        DEFAULT 'Dispatch Alert',
    `pushover_sound`       varchar(255)        DEFAULT 'pushover',
    FOREIGN KEY (`system_id`) REFERENCES `radio_systems` (`system_id`) ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `radio_system_telegram_settings`
(
    `telegram_setting_id` int(11) AUTO_INCREMENT PRIMARY KEY,
    `system_id`           int(11),
    `telegram_enabled`    tinyint(1) NOT NULL DEFAULT 0,
    `telegram_bot_token`  varchar(255)        DEFAULT NULL,
    `telegram_channel_id` varchar(128)        DEFAULT NULL,
    FOREIGN KEY (`system_id`) REFERENCES `radio_systems` (`system_id`) ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `radio_system_webhook_settings`
(
    `system_webhook_id` int(11) AUTO_INCREMENT PRIMARY KEY,
    `system_id`         int(11),
    `webhook_url`       varchar(255)        DEFAULT NULL,
    `webhook_headers`   TEXT,
    `webhook_enabled`   tinyint(1) NOT NULL DEFAULT 0,
    FOREIGN KEY (`system_id`) REFERENCES `radio_systems` (`system_id`) ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `radio_system_emails`
(
    `email_id`      int(11) AUTO_INCREMENT PRIMARY KEY,
    `system_id`     int(11),
    `email_address` varchar(255) NOT NULL,
    `email_enabled` tinyint(4)   NOT NULL DEFAULT 1,
    FOREIGN KEY (`system_id`) REFERENCES `radio_systems` (`system_id`) ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci;

-- create alert triggers table
CREATE TABLE IF NOT EXISTS `alert_triggers`
(
    `trigger_id`         int(11) AUTO_INCREMENT PRIMARY KEY,
    `system_id`          int(11)       NOT NULL,
    `trigger_name`       varchar(128)           DEFAULT NULL,
    `two_tone_a`         decimal(6, 1)          DEFAULT NULL,
    `two_tone_a_length`  int(11)                DEFAULT NULL,
    `two_tone_b`         decimal(6, 1)          DEFAULT NULL,
    `two_tone_b_length`  int(11)                DEFAULT NULL,
    `long_tone`          decimal(6, 1)          DEFAULT NULL,
    `long_tone_length`   int(11)                DEFAULT NULL,
    `hi_low_tone_a`      decimal(6, 1)          DEFAULT NULL,
    `hi_low_tone_b`      decimal(6, 1)          DEFAULT NULL,
    `alert_filter_id`    int(11)                DEFAULT NULL,
    `tone_tolerance`     int(11)       NOT NULL DEFAULT 2,
    `ignore_time`        decimal(6, 1) NOT NULL DEFAULT 300.0,
    `trigger_stream_url` varchar(512)           DEFAULT NULL,
    FOREIGN KEY (`system_id`) REFERENCES `radio_systems` (`system_id`) ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci;

-- create alert trigger emails table
CREATE TABLE IF NOT EXISTS `alert_trigger_emails`
(
    `email_id`      int(11) AUTO_INCREMENT PRIMARY KEY,
    `trigger_id`    int(11)      NOT NULL,
    `email_address` varchar(255) NOT NULL,
    `email_enabled` tinyint(4)   NOT NULL DEFAULT 1,
    FOREIGN KEY (`trigger_id`) REFERENCES `alert_triggers` (`trigger_id`) ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci;

-- create alert trigger webhooks table
CREATE TABLE IF NOT EXISTS `alert_trigger_webhooks`
(
    `trigger_webhook_id` int(11) AUTO_INCREMENT PRIMARY KEY,
    `trigger_id`         int(11)    NOT NULL,
    `webhook_url`        varchar(512)        DEFAULT NULL,
    `webhook_headers`    TEXT,
    `webhook_enabled`    tinyint(4) NOT NULL DEFAULT 1,
    FOREIGN KEY (`trigger_id`) REFERENCES `alert_triggers` (`trigger_id`) ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci;