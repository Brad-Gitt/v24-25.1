-- start: Kryptert init-data for bidrag-databasen i steg 9 - oppfyller F3 (persistens) og NF7 (kryptering av data at rest) (person 4 og person 5)
CREATE TABLE Bidrag (
  pseudonym        VARCHAR(200) PRIMARY KEY,
  salt             VARCHAR(11),
  passordhash      VARCHAR(44),
  kommentar        VARCHAR(1000),
  offentlig_nokkel VARCHAR(200),
  tittel           VARCHAR(100),
  tekst            VARCHAR(1000)
);

INSERT INTO Bidrag (pseudonym, salt, passordhash) VALUES
  ('osiedahs', '1712167670', 'Aw16YyLRWTS0BOoOb7DpvBMeYb444g.kl1a542GYpJA'),
  ('uozaixav', '1712167671', '5lQnfx89dpJpeaVR3CqCqy3pQPhdN8Nf0Nt9H9psgQ4'),
  ('olaebaev', '1712167672', '9tkRE7Q8yBj.ydZTxSCR3ZW8vzHtNOoSpWSK/ZepxUA');
  
-- slutt: Kryptert init-data for bidrag-databasen i steg 9 - oppfyller F3 (persistens) og NF7 (kryptering av data at rest) (person 4 og person 5)
