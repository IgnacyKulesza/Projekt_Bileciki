from flask import Flask,render_template,request,redirect,url_for,session,jsonify
from datetime import datetime
import psycopg
import edycja_danych as edycja
import odbieranie_danych as odbieranie
from config import Config
import hmac

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
app.secret_key = Config.SESSION_KEY


# zrobić dla każdej strony
@app.route('/')
def index():
    return render_template('index.html', message='')

@app.route('/strona-glowna')
def strona_glowna():
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
        )
    else:
        return render_template('index.html', message = 'Nie zalogowany')

@app.route('/koncerty')
def koncerty():
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
        )
    else:
        return render_template('index.html', message = 'Nie zalogowany')

@app.route('/bilety')
def bilety():
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
        )
    else:
        return render_template('index.html', message = 'Nie zalogowany')
    

@app.route('/ustawienia')
def ustawienia():
    if(session.get('logged')):
        return render_template('ustawienia.html')
    else:
        return render_template('index.html', message = 'Nie zalogowany')
    

@app.route("/login",methods = ['POST'])
def login():
    print(request.form)
    username = request.form.get('username') or ''
    password = request.form.get('password') or ''
    if hmac.compare_digest(username, Config.USERNAME or '') and hmac.compare_digest(password, Config.PASSWORD or ''):
        session['logged'] = True
        return redirect(url_for('strona_glowna'))
    else:
        return render_template('index.html', message='Nieprawidłowy email lub hasło'), 401

@app.route("/logout")
def logout():
    session.clear()
    return render_template('index.html', message = '')
# submitowanie danych do serwera
@app.route('/submit_koncerty',methods=['POST'])
def approute_koncerty():
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
            print(error)
            raise
        finally:
            kursor.close()
            polaczenie.close()

        return redirect(url_for('koncerty'))
    except ValueError as error:
        return redirect(url_for('koncerty', message=str(error)))
    except Exception:
        app.logger.exception('Nie udało się zapisać koncertu')
        return redirect(url_for('koncerty', message='Nie udało się zapisać koncertu. Sprawdź dane i spróbuj ponownie.'))


# submitowanie danych do serwera
@app.route('/submit_bilety',methods=['POST'])
def approute_bilety():
    id_biletu = request.form['id_biletu']
    czy_zeskanowane = request.form['czy_zeskanowane']
    imie = request.form['imie']
    nazwisko = request.form['nazwisko']
    id_koncertu = request.form['id_koncertu']

    polaczenie,kursor = postgres()
    edycja.insert(kursor,"Bilety",id_biletu,czy_zeskanowane,imie,nazwisko,id_koncertu)
    polaczenie.commit()
    kursor.close()
    polaczenie.close()

    return redirect(url_for('bilety'))


# usuwanie danych
@app.route('/submit_usun', methods=['POST'])
def submit_dane():
    tabela = request.form['tabela']
    usuwane = request.form['id']
    polaczenie,kursor = postgres()
    edycja.delete(kursor,tabela,int(usuwane))
    polaczenie.commit()
    kursor.close()
    polaczenie.close()

    return redirect(url_for('usundane'))


# edycja danych
# @app.route('/get_bilety', methods=[])

if __name__ == "__main__": app.run(debug=True)