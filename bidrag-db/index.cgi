#!/bin/sh

DB=../bidrag.db

# start: Person 2 – innhold + visninger (F1, F2, NF1)
url_param() {
    KEY="$1"
    echo "$QUERY_STRING" | tr '&' '\n' | awk -F= -v k="$KEY" '$1==k { print substr($0, index($0, "=")+1); exit }'
}

trim() {
    printf '%s' "$1" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//'
}

sql_escape() {
    printf '%s' "$1" | sed "s/'/''/g"
}

xml_felt() {
    FELT="$1"
    printf '%s' "$KR" | xmllint --xpath "string(/bidrag/$FELT)" - 2>/dev/null
}

valider_lengde() {
    FELTNAVN="$1"
    VERDI="$2"
    MAKS="$3"
    ANTALL=$(printf '%s' "$VERDI" | wc -c | tr -d ' ')

    if [ "$ANTALL" -gt "$MAKS" ]; then
        echo "$FELTNAVN er for lang (maks $MAKS tegn)."
        exit 1
    fi
}

valider_innhold() {
    T=$(trim "$T")
    K=$(trim "$K")
    X=$(trim "$X")
    O=$(trim "$O")

    valider_lengde "Pseudonym" "$N" 200
    valider_lengde "Tittel" "$T" 100
    valider_lengde "Kommentar" "$K" 1000
    valider_lengde "Tekst" "$X" 1000
    valider_lengde "Offentlig nøkkel" "$O" 200

    if [ -z "$T" ] && [ -z "$X" ]; then
        echo "Minst ett av feltene tittel eller tekst må fylles ut."
        exit 1
    fi
}

autentiser_bidragseier() {
    PN="$1"
    PW="$2"

    if [ -z "$PN" ] || [ -z "$PW" ]; then
        return 1
    fi

    PN_SQL=$(sql_escape "$PN")
    S=$(sqlite3 "$DB" "SELECT salt FROM Bidrag WHERE pseudonym='$PN_SQL'")
    if [ -z "$S" ]; then
        return 1
    fi

    H1=$(mkpasswd -m sha-256 -S "$S" "$PW" | cut -f4 -d$)
    H2=$(sqlite3 "$DB" "SELECT passordhash FROM Bidrag WHERE pseudonym='$PN_SQL'")

    [ "$H1" = "$H2" ]
}

vis_offentlig_liste() {
    sqlite3 -line "$DB" "
        SELECT
            coalesce(trim(tittel), '') AS tittel,
            coalesce(trim(tekst), '') AS tekst
        FROM Bidrag
        WHERE length(trim(coalesce(tittel, ''))) > 0
           OR length(trim(coalesce(tekst, ''))) > 0
        ORDER BY rowid DESC
    "
}

vis_admin_liste() {
    sqlite3 -line "$DB" "
        SELECT
            pseudonym AS pseudonym,
            coalesce(trim(tittel), '') AS tittel,
            coalesce(trim(tekst), '') AS tekst
        FROM Bidrag
        WHERE length(trim(coalesce(tittel, ''))) > 0
           OR length(trim(coalesce(tekst, ''))) > 0
        ORDER BY rowid DESC
    "
}

vis_min_visning() {
    PN_SQL=$(sql_escape "$1")
    sqlite3 -line "$DB" "
        SELECT
            pseudonym AS pseudonym,
            coalesce(trim(tittel), '') AS tittel,
            coalesce(trim(tekst), '') AS tekst,
            coalesce(kommentar, '') AS kommentar
        FROM Bidrag
        WHERE pseudonym='$PN_SQL'
        LIMIT 1
    "
}

logg_innholdsoperasjon() {
    HAR_TITTEL=nei
    HAR_TEKST=nei
    HAR_KOMMENTAR=nei

    if [ -n "$T" ]; then HAR_TITTEL=ja; fi
    if [ -n "$X" ]; then HAR_TEKST=ja; fi
    if [ -n "$K" ]; then HAR_KOMMENTAR=ja; fi

    echo "bidrag-db $REQUEST_METHOD visning=${VISNING:-skriv} tittel=$HAR_TITTEL tekst=$HAR_TEKST kommentar=$HAR_KOMMENTAR" >&2
}
# slutt: Person 2 – innhold + visninger (F1, F2, NF1)

# Skriver slutten av HTTP-hodet og en tom linje
cat <<EOF
Access-Control-Allow-Origin: http://localhost:8080
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET,POST,PUT,DELETE,OPTIONS
Access-Control-Allow-Headers: Content-Type
Content-Type:text/plain;charset=utf-8

EOF

# Omgar bug i httpd
CONTENT_LENGTH=$HTTP_CONTENT_LENGTH$CONTENT_LENGTH

if [ "$REQUEST_METHOD" = "OPTIONS" ]; then
    exit
fi

if [ "$REQUEST_METHOD" = "GET" ]; then
    VISNING=$(url_param visning)

    if [ -z "$VISNING" ] || [ "$VISNING" = "offentlig" ]; then
        vis_offentlig_liste
        exit
    fi

    if [ "$VISNING" = "admin" ]; then
        vis_admin_liste
        exit
    fi

    if [ "$VISNING" = "min" ]; then
        N=$(url_param navn)
        P=$(url_param passord)

        if autentiser_bidragseier "$N" "$P"; then
            vis_min_visning "$N"
        else
            echo "Autentisering feilet."
        fi
        exit
    fi

    echo "Ukjent visning."
    exit
fi

KR=$(head -c "$CONTENT_LENGTH")

N=$(xml_felt navn)
P=$(xml_felt passord)
K=$(xml_felt kommentar)
O=$(xml_felt offentlig_nokkel)
T=$(xml_felt tittel)
X=$(xml_felt tekst)

logg_innholdsoperasjon

if [ -z "$N" ]; then
    echo "Pseudonym mangler!"
    exit
fi

if [ "$REQUEST_METHOD" = "POST" ]; then
    if [ -n "$P" ]; then
        valider_innhold
        N_SQL=$(sql_escape "$N")
        K_SQL=$(sql_escape "$K")
        O_SQL=$(sql_escape "$O")
        T_SQL=$(sql_escape "$T")
        X_SQL=$(sql_escape "$X")

        FINNES=$(sqlite3 "$DB" "SELECT 1 FROM Bidrag WHERE pseudonym='$N_SQL'")
        if [ -n "$FINNES" ]; then
            echo "Bidrag finnes allerede for dette pseudonymet. Bruk Endre."
            exit
        fi

        # Lager et tilfeldig 11-sifret tall som salt (POSIX-vennlig)
        S=$(tr -dc '0-9' </dev/urandom | head -c 11)

        # Lager en hashverdi av det skapte saltet og det innsendte passordet
        H=$(mkpasswd -m sha-256 -S "$S" "$P" | cut -f4 -d$)

        sqlite3 "$DB" "
            INSERT INTO Bidrag (pseudonym, salt, passordhash, kommentar, offentlig_nokkel, tittel, tekst)
            VALUES ('$N_SQL', '$S', '$H', '$K_SQL', '$O_SQL', '$T_SQL', '$X_SQL')
        "
    fi
    exit
fi

# Henter lagret saltverdi
N_SQL=$(sql_escape "$N")
S=$(sqlite3 "$DB" "SELECT salt FROM Bidrag WHERE pseudonym='$N_SQL'")
if [ -z "$S" ]; then echo "Salt mangler" ; exit; fi

# Beregner hashverdi av innsendt passord
H1=$(mkpasswd -m sha-256 -S "$S" "$P" | cut -f4 -d$)

# Sammenligner med lagret hashverdi
H2=$(sqlite3 "$DB" "SELECT passordhash FROM Bidrag WHERE pseudonym='$N_SQL'")

# Avslutter om hashverdiene ikke er like 
if [ "$H1" != "$H2" ]; then echo "Feil passord!" >&2 ; exit; fi

if [ "$REQUEST_METHOD" = "DELETE" ]; then
    sqlite3 "$DB" "DELETE FROM Bidrag WHERE pseudonym='$N_SQL'"

elif [ "$REQUEST_METHOD" = "PUT" ]; then
    valider_innhold
    K_SQL=$(sql_escape "$K")
    O_SQL=$(sql_escape "$O")
    T_SQL=$(sql_escape "$T")
    X_SQL=$(sql_escape "$X")

    sqlite3 "$DB" "
       UPDATE Bidrag SET
           kommentar='$K_SQL',
           offentlig_nokkel='$O_SQL',
           tittel='$T_SQL',
           tekst='$X_SQL'
       WHERE pseudonym='$N_SQL'"
fi
