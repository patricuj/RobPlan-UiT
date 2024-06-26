-- MySQL Script generated by MySQL Workbench
-- Fri Apr 12 01:09:55 2024
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema myDb
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema myDb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `myDb` DEFAULT CHARACTER SET utf8 ;
USE `myDb` ;

-- -----------------------------------------------------
-- Table `myDb`.`Users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `myDb`.`Users`;

CREATE TABLE IF NOT EXISTS `myDb`.`Users` (
  `idUser` INT NOT NULL AUTO_INCREMENT,
  `Username` VARCHAR(45) NOT NULL,
  `Password` VARCHAR(255) NOT NULL,
  `Email` VARCHAR(255) NULL,
  PRIMARY KEY (`idUser`)
) ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `myDb`.`Notifications`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `myDb`.`Notifications`;

CREATE TABLE IF NOT EXISTS `myDb`.`Notifications` (
  `idNotifications` INT NOT NULL AUTO_INCREMENT,
  `Type` VARCHAR(100) NOT NULL,
  `Severity` VARCHAR(100) NOT NULL,
  `Message` MEDIUMTEXT NOT NULL,
  `Details` TEXT,
  `Timestamp` DATETIME NOT NULL,
  `IsRead` TINYINT NOT NULL,
  `Users_idUser` INT NOT NULL,
  `isar_id` VARCHAR(36),
  PRIMARY KEY (`idNotifications`),
  INDEX `fk_Notifications_Users_idx` (`Users_idUser` ASC) VISIBLE,
  CONSTRAINT `fk_Notifications_Users`
    FOREIGN KEY (`Users_idUser`)
    REFERENCES `myDb`.`Users` (`idUser`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `myDb`.`Missions`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `myDb`.`Missions`;

CREATE TABLE IF NOT EXISTS `myDb`.`Missions` (
  `idMission` INT NOT NULL AUTO_INCREMENT,
  `MissionName` VARCHAR(255) NOT NULL,
  `MissionData` TEXT NOT NULL,
  `IsAvailable` TINYINT NOT NULL DEFAULT 1,
  `Port` INT NOT NULL,
  `Status` VARCHAR(255) DEFAULT 'Ingen planlagt inspeksjon',
  `LastCompleted` DATETIME DEFAULT NULL,
  `Deadline` DATETIME DEFAULT NULL,
  PRIMARY KEY (`idMission`)
) ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `myDb`.`Results`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `myDb`.`Results`;

CREATE TABLE IF NOT EXISTS `myDb`.`Results` (
  `idResult` INT NOT NULL AUTO_INCREMENT,
  `MissionName` VARCHAR(255) NOT NULL,
  `RobotName` VARCHAR(255) NOT NULL,
  `Status` VARCHAR(50) NOT NULL,
  `Timestamp` DATETIME NOT NULL,
  `Details` TEXT,
  PRIMARY KEY (`idResult`)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `myDb`.`RobotInfo`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `myDb`.`RobotInfo`;

CREATE TABLE IF NOT EXISTS `RobotInfo` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `isar_id` VARCHAR(36) NOT NULL,
  `robot_name` VARCHAR(255) NOT NULL,
  `battery_level` FLOAT,
  `robot_status` VARCHAR(255),
  `current_mission_id` VARCHAR(255),
  `port` INT,
  `Timestamp` DATETIME NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

