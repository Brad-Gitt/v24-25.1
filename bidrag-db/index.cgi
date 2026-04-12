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

xml_escape() {
    printf '%s' "$1" | sed \
        -e 's/&/\&amp;/g' \
        -e 's/</\&lt;/g' \
        -e 's/>/\&gt;/g' \
        -e 's/"/\&quot;/g' \
        -e "s/'/\&apos;/g"
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

    H1=$(mkpasswd -m sha-256 -S "$S" "$PW" | cut -f4 -d'$')
    H2=$(sqlite3 "$DB" "SELECT passordhash FROM Bidrag WHERE pseudonym='$PN_SQL'")

    [ "$H1" = "$H2" ]
}

# start: Skiller mellom manglende bidrag og autentiseringsfeil i Min-visning - oppfyller F1 (identitet og flyt) og NF1 (integritet i tilbakemeldinger) (person 1 og person 2)
har_bidrag() {
    PN_SQL=$(sql_escape "$1")
    sqlite3 "$DB" "SELECT 1 FROM Bidrag WHERE pseudonym='$PN_SQL' LIMIT 1"
}
# slutt: Skiller mellom manglende bidrag og autentiseringsfeil i Min-visning - oppfyller F1 (identitet og flyt) og NF1 (integritet i tilbakemeldinger) (person 1 og person 2)

# start: Admin-autorisering med dobbel sjekk mot pseudonym-db - oppfyller F2 (admin-visning med pseudonym) og NF1 (forsvar i dybden) (person 3 og person 5)
er_adminbruker() {
    PN="$1"
    EPOST="$2"
    PASSORD="$3"

    if [ "$PN" != "admin" ] || [ -z "$EPOST" ] || [ -z "$PASSORD" ]; then
        return 1
    fi

    XML_PN="<pseudonym>
<epost>$(xml_escape "$EPOST")</epost>
<passord>$(xml_escape "$PASSORD")</passord>
</pseudonym>"

    SVAR=$(curl -s -d "$XML_PN" "http://allpodd:83/cgi-bin/index.cgi")
    [ "$SVAR" = "admin" ]
}
# slutt: Admin-autorisering med dobbel sjekk mot pseudonym-db - oppfyller F2 (admin-visning med pseudonym) og NF1 (forsvar i dybden) (person 3 og person 5)

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

cat <<EOF
Access-Control-Allow-Origin: http://localhost:8080
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET,POST,PUT,DELETE,OPTIONS
Access-Control-Allow-Headers: Content-Type
Content-Type:text/plain;charset=utf-8

EOF

CONTENT_LENGTH=$HTTP_CONTENT_LENGTH$CONTENT_LENGTH

if [ "$REQUEST_METHOD" = "OPTIONS" ]; then
    exit
fi

if [ "$REQUEST_METHOD" = "GET" ]; then
    VISNING=$(url_param visning)

    if [ -z "$VISNING" ]; then
        VISNING=$(url_param handling)
    fi

    if [ -z "$VISNING" ] || [ "$VISNING" = "offentlig" ] || [ "$VISNING" = "Liste" ]; then
        vis_offentlig_liste
        exit
    fi

    if [ "$VISNING" = "admin" ]; then
        N=$(url_param navn)
        E=$(url_param epost)
        P=$(url_param passord)

        if er_adminbruker "$N" "$E" "$P"; then
            vis_admin_liste
        else
            echo "Ingen tilgang til admin."
        fi
        exit
    fi

    if [ "$VISNING" = "min" ] || [ "$VISNING" = "Min" ]; then
        N=$(url_param navn)
        P=$(url_param passord)

        if [ -z "$(har_bidrag "$N")" ]; then
            echo "Ingen data funnet for brukeren."
        elif autentiser_bidragseier "$N" "$P"; then
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
N=$(trim "$N") # Person 1 fjernet whitespace fra pseudonym så DB matcher
echo "DEBUG navn=$N" >&2
E=$(xml_felt epost)
P=$(xml_felt passord)
K=$(xml_felt kommentar)
O=$(xml_felt offentlig_nokkel)
T=$(xml_felt tittel)
X=$(xml_felt tekst)
HND=$(xml_felt handling)

logg_innholdsoperasjon

if [ "$HND" = "Min" ]; then
    if [ -z "$(har_bidrag "$N")" ]; then
        echo "Ingen data funnet for brukeren."
    elif autentiser_bidragseier "$N" "$P"; then
        vis_min_visning "$N"
    else
        echo "Autentisering feilet."
    fi
    exit
fi

if [ "$HND" = "Liste" ]; then
    vis_offentlig_liste
    exit
fi

if [ "$HND" = "Admin" ]; then
    if er_adminbruker "$N" "$E" "$P"; then
        vis_admin_liste
    else
        echo "Ingen tilgang til admin."
    fi
    exit
fi

if [ -z "$N" ]; then
    echo "Pseudonym mangler!"
    exit
fi

if [ "$REQUEST_METHOD" = "POST" ]; then
    if [ "$HND" = "Slett" ]; then REQUEST_METHOD="DELETE"; fi
    if [ "$HND" = "Endre" ]; then REQUEST_METHOD="PUT"; fi
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

        S=$(tr -dc '0-9' </dev/urandom | head -c 11)
        H=$(mkpasswd -m sha-256 -S "$S" "$P" | cut -f4 -d'$')

        sqlite3 "$DB" "
            INSERT INTO Bidrag (pseudonym, salt, passordhash, kommentar, offentlig_nokkel, tittel, tekst)
            VALUES ('$N_SQL', '$S', '$H', '$K_SQL', '$O_SQL', '$T_SQL', '$X_SQL')
        "
    fi
    exit
fi

N_SQL=$(sql_escape "$N")
S=$(sqlite3 "$DB" "SELECT salt FROM Bidrag WHERE pseudonym='$N_SQL'")
if [ -z "$S" ]; then echo "Salt mangler" ; exit; fi

H1=$(mkpasswd -m sha-256 -S "$S" "$P" | cut -f4 -d'$')
H2=$(sqlite3 "$DB" "SELECT passordhash FROM Bidrag WHERE pseudonym='$N_SQL'")

if [ "$H1" != "$H2" ]; then echo "Feil passord!" >&2 ; exit; fi

case "$REQUEST_METHOD" in
    DELETE)
        sqlite3 "$DB" "DELETE FROM Bidrag WHERE pseudonym='$N_SQL'"
        ;;
    PUT)
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
        ;;
esac
