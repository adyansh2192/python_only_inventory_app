CREATE DATABASE IF NOT EXISTS inventory_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'inventory_app'@'localhost'
  IDENTIFIED BY 'ChangeMe_Strong_2026';

ALTER USER 'inventory_app'@'localhost'
  IDENTIFIED BY 'ChangeMe_Strong_2026';

GRANT SELECT, INSERT, UPDATE, DELETE
  ON inventory_db.*
  TO 'inventory_app'@'localhost';

FLUSH PRIVILEGES;

USE inventory_db;

CREATE TABLE IF NOT EXISTS items (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(120) NOT NULL,
  quantity INT UNSIGNED NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

INSERT INTO items (name, quantity)
VALUES ('Demo item', 3);
