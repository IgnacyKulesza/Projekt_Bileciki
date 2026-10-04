import psycopg
from config import Config

CONCERTS_PER_PAGE = 5
TICKETS_PER_PAGE = 5

# def postgres():

#     polaczenie=psycopg.connect(
#         host=Config.DATABASE_HOST,
#         port=Config.DATABASE_PORT,
#         database= Config.DATABASE_NAME,
#         user=Config.DATABASE_USER,
#         password=Config.DATABASE_PASSWORD
#     )

#     kursor=polaczenie.cursor()
#     return polaczenie,kursor

def getData(kursor,tabela,kolumna):
    kursor.execute(f'SELECT {kolumna} FROM {tabela}')
    dane = kursor.fetchall()

    return dane

def getConcertCount(kursor):
    kursor.execute('SELECT COUNT(*) FROM Koncerty')
    return kursor.fetchone()[0]


def getDataConcerts(kursor, strona):
    offset = (strona - 1) * CONCERTS_PER_PAGE

    kursor.execute(
        """
        SELECT nazwa, czas, zespol, ilosc_biletow
        FROM Koncerty
        ORDER BY czas, id_koncertu
        LIMIT %s OFFSET %s
        """,
        (CONCERTS_PER_PAGE, offset)
    )
    return kursor.fetchall()


def getTicketCount(kursor, czy_wygenerowany):
    kursor.execute('SELECT COUNT(*) FROM Bilety WHERE czy_zeskanowane = %s', (czy_wygenerowany,))
    return kursor.fetchone()[0]


def getDataTickets(kursor, strona, czy_wygenerowany):
    offset = (strona - 1) * TICKETS_PER_PAGE

    kursor.execute(
        """
        SELECT Koncerty.nazwa, Bilety.imie, Bilety.nazwisko,
             Koncerty.czas, Bilety.id_biletu, Bilety.czy_zeskanowane
        FROM Bilety
        JOIN Koncerty ON Bilety.id_koncertu = Koncerty.id_koncertu
        WHERE Bilety.czy_zeskanowane = %s
        ORDER BY Bilety.id_biletu
        LIMIT %s OFFSET %s
        """,
        (czy_wygenerowany, TICKETS_PER_PAGE, offset)
    )
    return kursor.fetchall()


def getIdConcert(kursor):
    kursor.execute('SELECT COALESCE(MAX(id_koncertu), 0) + 1 FROM Koncerty')
    return kursor.fetchone()[0]



# polaczenie,kursor = postgres()
# polaczenie.commit()
# kursor.close()
# polaczenie.close()
