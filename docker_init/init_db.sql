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
    `email_address_from`  varchar(255)        DEFAULT 'dispatch@example.com',
    `email_text_from`     varchar(255)        DEFAULT 'iCAD Dispatch',
    `email_alert_subject` varchar(512)        DEFAULT 'Dispatch Alert',
    `email_alert_body`    varchar(2048)                DEFAULT '{trigger_list} Alert at {timestamp}<br><br>{transcript}<br><br><a href="{audio_url}">Click for Dispatch Audio</a><br><br><a href="{stream_url}">Click Audio Stream</a>',
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
    `pushover_body`        varchar(2048)                DEFAULT '<font color="red"><b>{trigger_list}</b></font><br><br><a href="{audio_url}">Click for Dispatch Audio</a><br><br><a href="{stream_url}">Click Audio Stream</a>',
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

CREATE TABLE IF NOT EXISTS `radio_system_facebook_settings`
(
    `facebook_setting_id`      int(11) AUTO_INCREMENT PRIMARY KEY,
    `system_id`                int(11),
    `facebook_enabled`         tinyint(1) NOT NULL DEFAULT 0,
    `facebook_page_id`         varchar(255)        DEFAULT NULL,
    `facebook_page_token`      varchar(512)        DEFAULT NULL,
    `facebook_comment_enabled` tinyint(1) NOT NULL DEFAULT 0,
    `facebook_post_body`       varchar(2048) DEFAULT '{timestamp} Departments:\n{trigger_list}\n\nDispatch Audio:\n{mp3_url}',
    `facebook_comment_body`    varchar(2048) DEFAULT '{transcript}\n{stream_url}',
    FOREIGN KEY (`system_id`) REFERENCES `radio_systems` (`system_id`) ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `radio_system_webhooks`
(
    `webhook_id` int(11) AUTO_INCREMENT PRIMARY KEY,
    `system_id`         int(11),
    `webhook_url`       varchar(255)        DEFAULT NULL,
    `webhook_headers`   TEXT,
    `webhook_body`   TEXT,
    `enabled`   tinyint(1) NOT NULL DEFAULT 0,
    FOREIGN KEY (`system_id`) REFERENCES `radio_systems` (`system_id`) ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `radio_system_emails`
(
    `email_id`      int(11) AUTO_INCREMENT PRIMARY KEY,
    `system_id`     int(11),
    `email_address` varchar(255) NOT NULL,
    `enabled` tinyint(4)   NOT NULL DEFAULT 1,
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
    `two_tone_a_length`  decimal(6, 1)          DEFAULT 0.8,
    `two_tone_b`         decimal(6, 1)          DEFAULT NULL,
    `two_tone_b_length`  decimal(6, 1)          DEFAULT 2.8,
    `long_tone`          decimal(6, 1)          DEFAULT NULL,
    `long_tone_length`   decimal(6, 1)          DEFAULT 3.8,
    `hi_low_tone_a`      decimal(6, 1)          DEFAULT NULL,
    `hi_low_tone_b`      decimal(6, 1)          DEFAULT NULL,
    `hi_low_alternations` int(11)               DEFAULT 4,
    `alert_filter_id`    int(11)                DEFAULT NULL,
    `tone_tolerance`     decimal(6, 1)          DEFAULT 2.0,
    `ignore_time`        decimal(6, 1) NOT NULL DEFAULT 300.0,
    `stream_url`         varchar(512)           DEFAULT NULL,
    `enable_facebook`    tinyint(1)    NOT NULL DEFAULT 0,
    `enable_telegram`    tinyint(1)    NOT NULL DEFAULT 0,
    `enabled`            tinyint(2)             DEFAULT 1,
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
    `enabled` tinyint(4)   NOT NULL DEFAULT 1,
    FOREIGN KEY (`trigger_id`) REFERENCES `alert_triggers` (`trigger_id`) ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `alert_trigger_pushover_settings`
(
    `pushover_settings_id`     int(11) AUTO_INCREMENT PRIMARY KEY,
    `trigger_id`               int(11)                NOT NULL,
    `pushover_group_token`     varchar(255)           DEFAULT NULL,
    `pushover_app_token`       varchar(255)           DEFAULT NULL,
    `pushover_subject`         varchar(512)           DEFAULT NULL,
    `pushover_body`            TEXT,
    `pushover_sound`           varchar(128)           DEFAULT NULL,
    FOREIGN KEY (`trigger_id`) REFERENCES `alert_triggers` (`trigger_id`) ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci;

-- create alert trigger webhooks tabl
CREATE TABLE IF NOT EXISTS `alert_trigger_webhooks`
(
    `webhook_id` int(11) AUTO_INCREMENT PRIMARY KEY,
    `trigger_id`         int(11)    NOT NULL,
    `webhook_url`        varchar(512)        DEFAULT NULL,
    `webhook_headers`    TEXT,
    `webhook_body`       TEXT,
    `enabled`    tinyint(4) NOT NULL DEFAULT 1,
    FOREIGN KEY (`trigger_id`) REFERENCES `alert_triggers` (`trigger_id`) ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `alert_trigger_filters`
(
    `alert_filter_id` int(11) AUTO_INCREMENT PRIMARY KEY,
    `alert_filter_name` VARCHAR(255) NOT NULL,
    `enabled` tinyint(4) NOT NULL DEFAULT 1
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS  `alert_trigger_filter_keywords`
(
    `keyword_id` int(11) AUTO_INCREMENT PRIMARY KEY,
    `alert_filter_id` INT NOT NULL,
    `keyword` VARCHAR(255) NOT NULL,
    `is_excluded` tinyint(4) NOT NULL DEFAULT 0,
    `enabled` tinyint(4) NOT NULL DEFAULT 1,
    FOREIGN KEY (alert_filter_id) REFERENCES `alert_trigger_filters` (`alert_filter_id`) ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_general_ci;