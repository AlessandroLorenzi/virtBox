#!/bin/zsh
psql -h localhost -U virtmaster -W template1   < init.sql
#psql -h localhost -U postgres   -W template1   < grant_virtmaster.sql
psql -h localhost -U postgres -W virtbox     < /usr/share/postgresql/contrib/pgcrypto.sql
psql -h localhost -U virtmaster -W virtbox     < functions.sql

