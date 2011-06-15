\c virtbox
DROP LANGUAGE plpgsql CASCADE;
CREATE LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION RegisterUser(
                    varchar(255),
                    varchar(255),
                    varchar(255),
                    varchar(255)
                ) RETURNS INTEGER AS $$
DECLARE
    username ALIAS FOR $1;
    name ALIAS FOR $2;
    surname ALIAS FOR $3;
    password ALIAS FOR $4;
    salt VARCHAR(26);
    flag  INT := 0;
BEGIN
    SELECT COUNT(*) INTO flag FROM vuser WHERE vuser.username = username;
    IF flag <> 0 THEN
       return 1;
    END IF;
    SELECT encode(digest(username||password, 'sha256'), 'hex')::varchar(26) into salt;
    INSERT INTO vuser VALUES (username, name, surname, salt);
    INSERT INTO user2usergroup VALUES(username, 'default');
    return 0;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION VerifyPassword(
                    varchar(255),
                    varchar(255)
                ) RETURNS INTEGER AS $$
DECLARE
    username ALIAS FOR $1;
    password ALIAS FOR $2;
    salt VARCHAR(26);
    flag  INT := 0;
BEGIN
    
    SELECT encode(digest(username||password, 'sha256'), 'hex')::varchar(26) into salt;
    
    SELECT COUNT(*) INTO flag FROM vuser WHERE vuser.username = username AND vuser.password=salt;
    IF flag = 1 THEN
       return 1;
    END IF;
    return 0;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION CreateGuest(
                    varchar(255),
                    varchar(255)
                ) RETURNS INTEGER AS $$
DECLARE
    name ALIAS FOR $1;
    username ALIAS FOR $2;
    flag INT;
BEGIN
    SELECT COUNT(*) INTO flag FROM guest WHERE guest.name = name;
    IF flag <> 0 THEN
       return 1;
    END IF;
    
    INSERT INTO guest VALUES (name, username, 0);
    INSERT INTO guest2guestgroup VALUES(name, 'default');
	INSERT into acl_g2u VALUES(username, name, 31);
    return 0;
END;
$$ LANGUAGE plpgsql;
