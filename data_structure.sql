CREATE DATABASE IF NOT EXISTS `rubbergoddess` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;
USE `rubbergoddess`;

CREATE TABLE IF NOT EXISTS `bot_karma` (
  `member_id` varchar(30) NOT NULL,
  `karma` int(11) DEFAULT NULL,
  `nick` text,
  PRIMARY KEY (`member_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `bot_karma_giving` (
  `member_id` varchar(30) NOT NULL,
  `positive` int(11) DEFAULT NULL,
  `negative` int(11) DEFAULT NULL,
  `nick` text,
  PRIMARY KEY (`member_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `bot_karma_emoji` (
  `emoji_id` varchar(50) UNIQUE,
  `value` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `users` (
  `login` varchar(64) UNIQUE,
  `discord_id` text,
  `code` text DEFAULT NULL,
  `group` text,
  `changed` text,
  `status` int(11) DEFAULT NULL,
  `comment` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `bot_reminders` (
  `reminderID` int NOT NULL AUTO_INCREMENT,
  `message` text DEFAULT NULL,
  `channelID` varchar(64) DEFAULT NULL,
  `remind_time` timedate DEFAULT NULL,
  PRIMARY KEY (`reminderID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `bot_people_to_remind` (
  `userID` varchar(50) NOT NULL,
  `reminderID` int NOT NULL,
  `private` BOOLEAN,
  FOREIGN KEY (`reminderID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
