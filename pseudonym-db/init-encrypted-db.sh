#!/bin/sh

set -eu

# start: Oppretter kryptert pseudonym-database fra secret-styrt nokkel i steg 9 - oppfyller F3 (persistens), NF1 (ingen hardkodede hemmeligheter) og NF7 (kryptering av data at rest og nokkelhandtering) (person 4 og person 5)
DB_PATH="${1:-/data/pseudonym.db}"
KEY_FILE="${2:-${PSEUDONYM_DB_KEY_FILE:-/run/secrets/storage/pseudonym-db-key}}"

sql_escape() {
  printf '%s' "$1" | sed "s/'/''/g"
}

mkdir -p "$(dirname "$DB_PATH")"

if [ -f "$DB_PATH" ]; then
  if sqlcipher "$DB_PATH" <<EOF >/dev/null 2>&1
PRAGMA key = '$KEY_SQL';
SELECT count(*) FROM sqlite_master;
EOF
  then
    chown 10001:10001 "$DB_PATH"
    chmod 660 "$DB_PATH"
    exit 0
  fi

  if ! dd if="$DB_PATH" bs=16 count=1 2>/dev/null | grep -q "SQLite format 3"; then
    echo "Eksisterende kryptert pseudonym-db kunne ikke apnes med gjeldende nokkel." >&2
    exit 1
  fi
fi

if [ ! -s "$KEY_FILE" ]; then
  echo "Manglende krypteringsnokkel for pseudonym-db." >&2
  exit 1
fi

KEY=$(tr -d '\r\n' < "$KEY_FILE")
KEY_SQL=$(sql_escape "$KEY")
TMP_DB="${DB_PATH}.tmp"
PLAIN_DB="${DB_PATH}.plain"

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

mv "$TMP_DB" "$DB_PATH"
trap - EXIT
chown 10001:10001 "$DB_PATH"
chmod 660 "$DB_PATH"
# slutt: Oppretter kryptert pseudonym-database fra secret-styrt nokkel i steg 9 - oppfyller F3 (persistens), NF1 (ingen hardkodede hemmeligheter) og NF7 (kryptering av data at rest og nokkelhandtering) (person 4 og person 5)
