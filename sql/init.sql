/*
 *      init.sql
 *      
 *      Copyright 2010 Alessandro Lorenzi <alessandro.lorenzi@gmail.com>
 *      
 */

DROP DATABASE virtbox;
CREATE DATABASE virtbox;

\c virtbox
 
 CREATE TABLE vuser
 (
	username 	VARCHAR(100) 		PRIMARY KEY NOT NULL  ,
	surname 	VARCHAR(100) NOT NULL  ,
	name 		VARCHAR(100) NOT NULL  ,
	password 	VARCHAR(26)
 );
CREATE TABLE guest
(
    name 		VARCHAR(100) 	PRIMARY KEY NOT NULL  ,
    id_owner 	VARCHAR(8)   	REFERENCES vuser(username) NOT NULL  ON DELETE CASCADE,
	template 	INT --yes/no
);

CREATE TABLE acl_g2u
(
	username     	VARCHAR(100)    REFERENCES vuser(username) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL  ,
	guest		   	VARCHAR(100)    REFERENCES guest(name) ON DELETE CASCADE ON UPDATE CASCADE,                              
	permissions 	int,
	PRIMARY KEY(username, guest)
);  


CREATE TABLE disk
(
	name 		VARCHAR(100)	PRIMARY KEY NOT NULL  ,
	uri 		VARCHAR(500) 	UNIQUE NOT NULL  ,
	md5			VARCHAR(32)
);

CREATE TABLE hdd_image
(
	name 		VARCHAR(100)	PRIMARY KEY NOT NULL 
);

CREATE TABLE usergroup
(
	name		varchar(100)	PRIMARY KEY,
	permissions	int
);


CREATE TABLE guestgroup
(
	name		varchar(100)	PRIMARY KEY,
	permissions	int
);

CREATE TABLE user2usergroup
(
	username	varchar(100) REFERENCES vuser(username) ON DELETE CASCADE,
	usergroup	varchar(100) REFERENCES usergroup(name) ON DELETE CASCADE,
	PRIMARY KEY(username, usergroup)
);
	
CREATE TABLE guest2guestgroup
(
	guest	 	varchar(100) REFERENCES guest(name) ON DELETE CASCADE,
	guestroup 	varchar(100) REFERENCES guestgroup(name) ON DELETE CASCADE,
	PRIMARY KEY(guest, guestroup)
);

INSERT INTO usergroup (name, permissions) VALUES ('default', '00000000');
INSERT INTO guestgroup (name, permissions) VALUES ('default', '00000000');

