/*
 *      init.sql
 *      
 *      Copyright 2010 Alessandro Lorenzi <alessandro.lorenzi@gmail.com>
 *      
 */
 
 CREATE TABLE utenti
 (
	matricola	INT 			PRIMARY KEY,
	cognome		VARCHAR(100),
	nome		VARCHAR(100),
	password	VARCHAR(32)
 )
 
CREATE TABLE gruppi
(
	id_gruppo	INT 			PRIMARY KEY,
	nome		INT,
	permessi	VARCHAR
)

CREATE TABLE ut2gru
(
	matricola	INT 			REFERENCES utenti(matricola),
	id_gruppo	INT				REFERENCES gruppi(id_gruppo),
	PRIMARY KEY (matricola, id_gruppo)
)

CREATE TABLE templates
(
	nome		VARCHAR(100)	PRIMARY KEY,
	descrizione	VARCHAR(500),
	xml_uri		VARCHAR(200),
	id_owner	INT 			REFERENCES utenti(matricola)
)

CREATE TABLE dischi_template
(
	id_disco	INT				PRIMARY KEY,
	id_template	INT				REFERENCES templates(id_template),
	uri			VARCHAR(200)
)

CREATE TABLE aule
(
	id_aula 	INT				PRIMARY KEY,
	id_owner	INT				REFERENCES utenti(matricola)
)

CREATE TABLE macchine
(
	nome		VARCHAR(100)	PRIMARY KEY,
	id_owner	INT				REFERENCES utenti(matricola),
	aula		INT				REFERENCES aule(id_aula)
)

CREATE TABLE dischi
(
	id_disco	INT				PRIMARY KEY,
	id_macchina	VARCHAR(100)	REFERENCES macchine(nome),
	uri			VARCHAR(100)		
)
