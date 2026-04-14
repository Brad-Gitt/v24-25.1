-- start: Kryptert init-data for pseudonym-databasen i steg 9 - oppfyller F3 (persistens) og NF7 (kryptering av data at rest) (person 4 og person 5)
CREATE TABLE Pseudonym (
  epost       VARCHAR(200) PRIMARY KEY,
  pseudonym   VARCHAR(200),
  salt        VARCHAR(11),
  passordhash VARCHAR(44)
);

INSERT INTO Pseudonym (epost, pseudonym, salt, passordhash) VALUES
  ('Ante@example.com', 'osiedahs', '1712167670', 'Aw16YyLRWTS0BOoOb7DpvBMeYb444g.kl1a542GYpJA'),
  ('Bjart@example.com', 'uozaixav', '1712167671', 'q37QpOdM2jSDeXOVAyiCSzMgy08dI7pLQ1aBElJps48'),
  ('Cecilie@example.com', 'olaebaev', '1712167672', 'D0z6dLRTSw.u7tct9zQVBUOCBhPEiFn2Eb./li.oyUA'),
  ('mikke@gmail.com', 'admin', '12345678901', 'x4kxRrzfJD4PBaEA6qKjP5Q7tl75ODtubn3zHpcyma9'),
  ('test_admin@usn.com', 'admin', '12345678902', 'bVNOzIEuSPJxlueGS8Xlx.nNCWkfcUfqn.MkuEqEKv0');
-- slutt: Kryptert init-data for pseudonym-databasen i steg 9 - oppfyller F3 (persistens) og NF7 (kryptering av data at rest) (person 4 og person 5)
