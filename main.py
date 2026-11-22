from flask import Flask,render_template,request,redirect,url_for,session,jsonify
from datetime import datetime
import psycopg
import edycja_danych as edycja
import odbieranie_danych as odbieranie
from config import Config
from wysylanie_biletow.generowanie_qr import gen_base64
import hmac
import secrets
from flasgger import Swagger

def postgres():

    polaczenie=psycopg.connect(
        host=Config.DATABASE_HOST,
        port=Config.DATABASE_PORT,
        dbname=Config.DATABASE_NAME,
        user=Config.DATABASE_USER,
        password=Config.DATABASE_PASSWORD
    )

    kursor=polaczenie.cursor()
    return polaczenie,kursor

app = Flask(__name__, template_folder="HTML", static_folder="HTML/static")
app.config["SWAGGER"] = {
    "title": "Bileciki API",
    "description": "API aplikacji do zarządzania koncertami i biletami",
    "version": "1.0.0",
    "uiversion": 3,
    "securityDefinitions": {
        "sessionCookie": {
            "type": "apiKey",
            "in": "cookie",
            "name": "session",
        }
    },
}
swagger = Swagger(app)
app.secret_key = Config.SESSION_KEY


# zrobić dla każdej strony
@app.route('/')
def index():
    """Zwraca stronę logowania.
    ---
    tags:
      - Pages
    produces:
      - text/html
    responses:
      200:
        description: Strona logowania została zwrócona.
    """
    return render_template('index.html', message=''), 200

@app.route('/strona-glowna')
def strona_glowna():
    """Zwraca stronę główną z listą koncertów.
    ---
    tags:
      - Pages
    produces:
      - text/html
    security:
      - sessionCookie: []
    parameters:
      - name: strona
        in: query
        type: integer
        minimum: 1
        default: 1
        description: Numer strony wyników.
    responses:
      200:
        description: Strona główna z paginowaną listą koncertów.
      401:
        description: Użytkownik nie jest zalogowany.
    """
    if(session.get('logged')):
        strona = max(1, request.args.get('strona', 1, type=int) or 1)
        polaczenie, kursor = postgres()
        try:
            liczba_koncertow = odbieranie.getConcertCount(kursor)
            liczba_stron = max(
                1,
                (liczba_koncertow + odbieranie.CONCERTS_PER_PAGE - 1)
                // odbieranie.CONCERTS_PER_PAGE
            )
            strona = min(strona, liczba_stron)
            koncerty = odbieranie.getDataConcerts(kursor, strona)
        finally:
            kursor.close()
            polaczenie.close()

        pierwszy_wynik = (strona - 1) * odbieranie.CONCERTS_PER_PAGE + 1
        if liczba_koncertow == 0:
            pierwszy_wynik = 0
        ostatni_wynik = min(strona * odbieranie.CONCERTS_PER_PAGE, liczba_koncertow)

        return render_template(
            'glowna.html',
            koncerty=koncerty,
            strona=strona,
            liczba_stron=liczba_stron,
            pierwszy_wynik=pierwszy_wynik,
            ostatni_wynik=ostatni_wynik,
            liczba_koncertow=liczba_koncertow,
        ), 200
    else:
        return render_template('index.html', message = 'Nie zalogowany'), 401

@app.route('/koncerty')
def koncerty():
    """Zwraca stronę zarządzania koncertami.
    ---
    tags:
      - Pages
    produces:
      - text/html
    security:
      - sessionCookie: []
    parameters:
      - name: strona
        in: query
        type: integer
        minimum: 1
        default: 1
      - name: message
        in: query
        type: string
        description: Komunikat po walidacji lub zapisie.
    responses:
      200:
        description: Lista koncertów i formularz tworzenia koncertu.
      401:
        description: Użytkownik nie jest zalogowany.
    """
    if(session.get('logged')):
        strona = max(1, request.args.get('strona', 1, type=int) or 1)
        polaczenie, kursor = postgres()
        try:
            liczba_koncertow = odbieranie.getConcertCount(kursor)
            liczba_stron = max(
                1,
                (liczba_koncertow + odbieranie.CONCERTS_PER_PAGE - 1)
                // odbieranie.CONCERTS_PER_PAGE
            )
            strona = min(strona, liczba_stron)
            koncerty = odbieranie.getDataConcerts(kursor, strona)
        finally:
            kursor.close()
            polaczenie.close()
        
        pierwszy_wynik = (strona - 1) * odbieranie.CONCERTS_PER_PAGE + 1
        if liczba_koncertow == 0:
            pierwszy_wynik = 0
        ostatni_wynik = min(strona * odbieranie.CONCERTS_PER_PAGE, liczba_koncertow)
        
        return render_template(
            'koncerty.html',
            koncerty=koncerty,
            strona=strona,
            liczba_stron=liczba_stron,
            pierwszy_wynik=pierwszy_wynik,
            ostatni_wynik=ostatni_wynik,
            liczba_koncertow=liczba_koncertow,
            message=request.args.get('message', ''),
        ),200
    else:
        return render_template('index.html', message = 'Nie zalogowany'), 401

@app.route('/bilety')
def bilety():
    """Zwraca stronę zarządzania biletami.
    ---
    tags:
      - Pages
    produces:
      - text/html
    security:
      - sessionCookie: []
    parameters:
      - name: status
        in: query
        type: string
        enum:
          - generated
          - not_generated
        default: not_generated
      - name: strona
        in: query
        type: integer
        minimum: 1
        default: 1
      - name: bilet_id
        in: query
        type: string
        description: Identyfikator biletu, który ma zostać wybrany.
    responses:
      200:
        description: Lista biletów i formularz tworzenia biletu.
      401:
        description: Użytkownik nie jest zalogowany.
    """
    if(session.get('logged')):
        status = request.args.get('status', 'not_generated')
        if status not in ('generated', 'not_generated'):
            status = 'not_generated'
        czy_wygenerowany = status == 'generated'
        strona = max(1, request.args.get('strona', 1, type=int) or 1)
        polaczenie, kursor = postgres()
        try:
            liczba_biletow = odbieranie.getTicketCount(kursor, czy_wygenerowany)
            liczba_stron = max(
                1,
                (liczba_biletow + odbieranie.TICKETS_PER_PAGE - 1)
                // odbieranie.TICKETS_PER_PAGE
            )
            strona = min(strona, liczba_stron)
            lista_biletow = odbieranie.getDataTickets(kursor, strona, czy_wygenerowany)
            polaczenie.commit()
        finally:
            kursor.close()
            polaczenie.close()

        bilet_id = request.args.get('bilet_id')
        wybrany_bilet = next(
            (bilet for bilet in lista_biletow if bilet[4] == bilet_id),
            lista_biletow[0] if lista_biletow else None,
        )
        pierwszy_wynik = (strona - 1) * odbieranie.TICKETS_PER_PAGE + 1
        if liczba_biletow == 0:
            pierwszy_wynik = 0
        ostatni_wynik = min(strona * odbieranie.TICKETS_PER_PAGE, liczba_biletow)

        return render_template(
            'bilety.html',
            lista_biletow=lista_biletow,
            wybrany_bilet=wybrany_bilet,
            status=status,
            strona=strona,
            liczba_stron=liczba_stron,
            pierwszy_wynik=pierwszy_wynik,
            ostatni_wynik=ostatni_wynik,
            liczba_biletow=liczba_biletow,
        ),200
    else:
        return render_template('index.html', message = 'Nie zalogowany'),401
    

@app.route('/ustawienia')
def ustawienia():
    """Zwraca stronę ustawień.
    ---
    tags:
      - Pages
    produces:
      - text/html
    security:
      - sessionCookie: []
    responses:
      200:
        description: Strona ustawień została zwrócona.
      401:
        description: Użytkownik nie jest zalogowany.
    """
    if(session.get('logged')):
        return render_template('ustawienia.html'), 200
    else:
        return render_template('index.html', message = 'Nie zalogowany'),401
    

@app.route("/login",methods = ['POST'])
def login():
    """Loguje użytkownika za pomocą adresu e-mail i hasła.
    ---
    tags:
      - Authentication
    consumes:
      - application/x-www-form-urlencoded
    parameters:
      - name: username
        in: formData
        type: string
        required: true
      - name: password
        in: formData
        type: string
        required: true
    responses:
      200:
        description: Login successful; redirects to the main page.
      401:
        description: Invalid email or password.
    """
    username = request.form.get('username') or ''
    password = request.form.get('password') or ''
    if hmac.compare_digest(username, Config.USERNAME or '') and hmac.compare_digest(password, Config.PASSWORD or ''):
        session['logged'] = True
        return redirect(url_for('strona_glowna')), 200
    else:
        return render_template('index.html', message='Nieprawidłowy email lub hasło'), 401

@app.route("/logout")
def logout():
    """Wylogowuje użytkownika i usuwa sesję.
    ---
    tags:
      - Authentication
    produces:
      - text/html
    security:
      - sessionCookie: []
    responses:
      200:
        description: Sesja została usunięta i zwrócono stronę logowania.
    """
    session.clear()
    return render_template('index.html', message = ''),200
# submitowanie danych do serwera
@app.route('/submit_koncerty', methods=['POST'])
def approute_koncerty():
    """
    Creates a concert.
    ---
    tags:
      - Concerts
    consumes:
      - application/x-www-form-urlencoded
    security:
      - sessionCookie: []
    parameters:
      - name: czas
        in: formData
        type: string
        format: date-time
        required: true
        example: "2027-06-15T19:00"
      - name: nazwa
        in: formData
        type: string
        minLength: 1
        maxLength: 31
        required: true
      - name: zespol
        in: formData
        type: string
        minLength: 1
        maxLength: 127
        required: true
      - name: opis
        in: formData
        type: string
        minLength: 1
        maxLength: 513
        required: true
      - name: ilosc_biletow
        in: formData
        type: integer
        minimum: 1
        maximum: 2147483647
        required: true
    responses:
      201:
        description: Concert created and user redirected.
      400:
        description: Invalid form data or database error.
    """
    try:
        try:
            czas = datetime.fromisoformat(request.form.get('czas', ''))
        except ValueError as error:
            raise ValueError('Wybierz prawidłową datę i godzinę.') from error

        nazwa = request.form.get('nazwa', '').strip()
        zespol = request.form.get('zespol', '').strip()
        opis = request.form.get('opis', '').strip()
        try:
            ilosc_biletow = int(request.form.get('ilosc_biletow', ''))
        except ValueError as error:
            raise ValueError('Podaj prawidłową liczbę biletów.') from error

        if not nazwa or len(nazwa) > 31:
            raise ValueError('Nazwa koncertu jest wymagana i może mieć maksymalnie 31 znaków.')
        if not zespol or len(zespol) > 127:
            raise ValueError('Nazwa zespołu jest wymagana i może mieć maksymalnie 127 znaków.')
        if not opis or len(opis) > 513:
            raise ValueError('Opis jest wymagany i może mieć maksymalnie 513 znaków.')
        if not 1 <= ilosc_biletow <= 2147483647:
            raise ValueError('Liczba biletów musi być większa od 0.')

        polaczenie,kursor = postgres()
        try:
            edycja.insert(kursor,'Koncerty',czas,nazwa,zespol,opis,ilosc_biletow)
            polaczenie.commit()
        except Exception as error:
            polaczenie.rollback()
            raise
        finally:
            kursor.close()
            polaczenie.close()

        return redirect(url_for('koncerty')), 201
    except ValueError as error:
        return redirect(url_for('koncerty', message=str(error))),400
    except Exception:
        app.logger.exception('Nie udało się zapisać koncertu')
        return redirect(url_for('koncerty', message='Nie udało się zapisać koncertu. Sprawdź dane i spróbuj ponownie.')), 400


# submitowanie danych do serwera
@app.route('/submit_bilety',methods=['POST'])
def approute_bilety():
    """Tworzy nowy bilet i generuje jego kod QR.
    ---
    tags:
      - Tickets
    consumes:
      - application/x-www-form-urlencoded
    produces:
      - text/html
    security:
      - sessionCookie: []
    parameters:
      - name: imie
        in: formData
        type: string
        maxLength: 31
        required: true
      - name: nazwisko
        in: formData
        type: string
        maxLength: 63
        required: true
      - name: id_koncertu
        in: formData
        type: integer
        required: true
    responses:
      201:
        description: Bilet został utworzony i użytkownik został przekierowany.
      400:
        description: Nieprawidłowe dane formularza.
      500:
        description: Nie udało się zapisać biletu lub wygenerować QR.
    """
    id_biletu = secrets.token_urlsafe(16)
    czy_zeskanowane = False
    imie = request.form['imie']
    nazwisko = request.form['nazwisko']
    id_koncertu = request.form['id_koncertu']
    qr = gen_base64(id_biletu)

    polaczenie,kursor = postgres()
    try:
        edycja.insert(
            kursor, "Bilety", id_biletu, czy_zeskanowane, imie, nazwisko, id_koncertu, qr
        )
        polaczenie.commit()
    except Exception:
        polaczenie.rollback()
        app.logger.exception('Nie udało się zapisać biletu')
        raise
    finally:
        kursor.close()
        polaczenie.close()

    return redirect(url_for('bilety')), 201


# usuwanie danych
@app.route('/submit_usun', methods=['POST'])
def submit_dane():
    """Usuwa koncert lub bilet według identyfikatora.
    ---
    tags:
      - Administration
    consumes:
      - application/x-www-form-urlencoded
    security:
      - sessionCookie: []
    parameters:
      - name: tabela
        in: formData
        type: string
        enum:
          - Koncerty
          - Bilety
        required: true
      - name: id
        in: formData
        type: integer
        required: true
        description: Identyfikator rekordu do usunięcia.
    responses:
      204:
        description: Rekord został usunięty i następuje przekierowanie.
      400:
        description: Nieprawidłowa tabela lub identyfikator.
      500:
        description: Nie udało się usunąć rekordu z bazy danych.
    """
    tabela = request.form['tabela']
    usuwane = request.form['id']
    polaczenie,kursor = postgres()
    edycja.delete(kursor,tabela,int(usuwane))
    polaczenie.commit()
    kursor.close()
    polaczenie.close()

    return redirect(url_for('usundane')),204


# edycja danych
# @app.route('/get_bilety', methods=[])

if __name__ == "__main__": app.run(debug=True)