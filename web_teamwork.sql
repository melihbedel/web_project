-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema web_teamwork
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema web_teamwork
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `web_teamwork` DEFAULT CHARACTER SET utf8mb4 ;
USE `web_teamwork` ;

-- -----------------------------------------------------
-- Table `web_teamwork`.`categories`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `web_teamwork`.`categories` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(30) NOT NULL,
  `description` VARCHAR(50) NOT NULL,
  `is_locked` TINYINT(1) NULL DEFAULT 0,
  `is_private` TINYINT(1) NULL DEFAULT 0,
  `created_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;


-- -----------------------------------------------------
-- Table `web_teamwork`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `web_teamwork`.`users` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(45) NOT NULL,
  `password` VARCHAR(99) NOT NULL,
  `role` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;


-- -----------------------------------------------------
-- Table `web_teamwork`.`messages`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `web_teamwork`.`messages` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `content` VARCHAR(250) NOT NULL,
  `timestamp` DATETIME NOT NULL,
  `sender_id` INT(11) NOT NULL,
  `receiver_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_messages_users1_idx` (`sender_id` ASC) VISIBLE,
  INDEX `fk_messages_users2_idx` (`receiver_id` ASC) VISIBLE,
  CONSTRAINT `fk_messages_users1`
    FOREIGN KEY (`sender_id`)
    REFERENCES `web_teamwork`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_messages_users2`
    FOREIGN KEY (`receiver_id`)
    REFERENCES `web_teamwork`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;


-- -----------------------------------------------------
-- Table `web_teamwork`.`topics`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `web_teamwork`.`topics` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(40) NOT NULL,
  `body` VARCHAR(300) NOT NULL,
  `category_id` INT(11) NOT NULL,
  `user_id` INT(11) NOT NULL,
  `is_locked` TINYINT(1) NULL DEFAULT 0,
  `is_private` TINYINT(1) NULL DEFAULT 0,
  `best_reply_id` INT(11) NULL DEFAULT NULL,
  `created_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_topics_categories_idx` (`category_id` ASC) VISIBLE,
  INDEX `fk_topics_users1_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_topics_categories`
    FOREIGN KEY (`category_id`)
    REFERENCES `web_teamwork`.`categories` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_topics_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `web_teamwork`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;


-- -----------------------------------------------------
-- Table `web_teamwork`.`replies`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `web_teamwork`.`replies` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `creation_date` DATETIME NOT NULL,
  `content` LONGTEXT NOT NULL,
  `topic_id` INT(11) NOT NULL,
  `user_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_replies_topics1_idx` (`topic_id` ASC) VISIBLE,
  INDEX `fk_replies_users1_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_replies_topics1`
    FOREIGN KEY (`topic_id`)
    REFERENCES `web_teamwork`.`topics` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_replies_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `web_teamwork`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;


-- -----------------------------------------------------
-- Table `web_teamwork`.`votes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `web_teamwork`.`votes` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `reply_id` INT(11) NOT NULL,
  `user_id` INT(11) NOT NULL,
  `vote` TINYINT(1) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_votes_replies_idx` (`reply_id` ASC) VISIBLE,
  INDEX `fk_votes_users1_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_votes_replies`
    FOREIGN KEY (`reply_id`)
    REFERENCES `web_teamwork`.`replies` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_votes_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `web_teamwork`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
