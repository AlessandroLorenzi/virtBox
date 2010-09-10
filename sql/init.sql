/*
 *      init.sql
 *      
 *      Copyright 2010 Alessandro Lorenzi <alessandro.lorenzi@gmail.com>
 *      
 */
 
 CREATE TABLE utenti
 (
	matricola 	INT 			PRIMARY KEY,
	cognome 	VARCHAR(100),
	nome 		VARCHAR(100),
	password 	VARCHAR(64)
 );
CREATE TABLE macchine
(
	nome 		VARCHAR(100) 	PRIMARY KEY,
	id_owner 	INT 			REFERENCES utenti(matricola),
	template 	INT --yes/no
);

CREATE TABLE acl_m2u
(
	matricola 		INT 			REFERENCES utenti(matricola),
	nome_macchina 	VARCHAR(100) 	REFERENCES macchine(nome),
	actio 			varchar(100),
	val 			int,
	PRIMARY KEY(matricola, nome_macchina, actio)		
);
