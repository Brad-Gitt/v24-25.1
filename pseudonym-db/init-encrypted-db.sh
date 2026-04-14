#!/bin/sh

set -eu

# start: Oppretter kryptert pseudonym-database fra secret-styrt nokkel i steg 9 - oppfyller F3 (persistens), NF1 (ingen hardkodede hemmeligheter) og NF7 (kryptering av data at rest og nokkelhandtering) (person 4 og person 5)
DB_PATH="${1:-/data/pseudonym.db}"
KEY_FILE="${2:-${PSEUDONYM_DB_KEY_FILE:-/run/secrets/storage/pseudonym-db-key}}"

sql_escape() {
  printf '%s' "$1" | sed "s/'/''/g"
}

mkdir -p "$(dirname "$DB_PATH")"

if [ ! -s "$KEY_FILE" ]; then
  echo "Manglende krypteringsnokkel for pseudonym-db." >&2
  exit 1
fi

KEY=$(tr -d '\r\n' < "$KEY_FILE")
KEY_SQL=$(sql_escape "$KEY")
TMP_DB="${DB_PATH}.tmp"
PLAIN_DB="${DB_PATH}.plain"

# start: Synkroniserer demo-brukere og kjente passord ved oppstart i steg 9 - oppfyller F1 (identitet og flyt), F3 (persistens) og NF7 (kryptert lagring) (person 4 og person 5)
synkroniser_demo_brukere() {
  TARGET_DB="$1"

  sqlcipher "$TARGET_DB" <<EOF
PRAGMA key = '$KEY_SQL';
INSERT INTO Pseudonym (epost, pseudonym, salt, passordhash) VALUES
  ('Ante@example.com', 'osiedahs', '1712167670', 'Aw16YyLRWTS0BOoOb7DpvBMeYb444g.kl1a542GYpJA'),
  ('Bjart@example.com', 'uozaixav', '1712167671', '5lQnfx89dpJpeaVR3CqCqy3pQPhdN8Nf0Nt9H9psgQ4'),
  ('Cecilie@example.com', 'olaebaev', '1712167672', '9tkRE7Q8yBj.ydZTxSCR3ZW8vzHtNOoSpWSK/ZepxUA'),
  ('mikke@gmail.com', 'admin', '12345678901', '3pxeb/.Vk9IUi/DI91E1PlBuFwIPNgoLbtVnG2sZIX7'),
  ('test_admin@usn.com', 'admin', '12345678902', 'pe.Rb1e7dwA7KccxIidKRw4gPoXp3qTxS83S4ITDVC7')
ON CONFLICT(epost) DO UPDATE SET
  pseudonym = excluded.pseudonym,
  salt = excluded.salt,
  passordhash = excluded.passordhash;
EOF
}
# slutt: Synkroniserer demo-brukere og kjente passord ved oppstart i steg 9 - oppfyller F1 (identitet og flyt), F3 (persistens) og NF7 (kryptert lagring) (person 4 og person 5)

if [ -f "$DB_PATH" ]; then
  if sqlcipher "$DB_PATH" <<EOF >/dev/null 2>&1
PRAGMA key = '$KEY_SQL';
SELECT count(*) FROM sqlite_master;
EOF
  then
    synkroniser_demo_brukere "$DB_PATH"
    chown 10001:10001 "$DB_PATH"
    chmod 660 "$DB_PATH"
    exit 0
  fi

  if ! dd if="$DB_PATH" bs=16 count=1 2>/dev/null | grep -q "SQLite format 3"; then
    echo "Eksisterende kryptert pseudonym-db kunne ikke apnes med gjeldende nokkel." >&2
    exit 1
  fi
fi

cleanup() {
  rm -f "$TMP_DB"
}

trap cleanup EXIT

if [ -f "$DB_PATH" ]; then
  mv "$DB_PATH" "$PLAIN_DB"

  sqlcipher "$PLAIN_DB" <<EOF
ATTACH DATABASE '$TMP_DB' AS encrypted KEY '$KEY_SQL';
SELECT sqlcipher_export('encrypted');
DETACH DATABASE encrypted;
EOF

  rm -f "$PLAIN_DB"
else
  sqlcipher "$TMP_DB" <<EOF
PRAGMA key = '$KEY_SQL';
.read /var/www/init.sql
EOF
fi

synkroniser_demo_brukere "$TMP_DB"

mv "$TMP_DB" "$DB_PATH"
trap - EXIT
chown 10001:10001 "$DB_PATH"
chmod 660 "$DB_PATH"
# slutt: Oppretter kryptert pseudonym-database fra secret-styrt nokkel i steg 9 - oppfyller F3 (persistens), NF1 (ingen hardkodede hemmeligheter) og NF7 (kryptering av data at rest og nokkelhandtering) (person 4 og person 5)
