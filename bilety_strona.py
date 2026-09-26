from flask import Flask,render_template,request,redirect,url_for,session,jsonify
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
    return render_template('index.html')

@app.route('/strona-glowna')
def strona_glowna():
    return render_template('glowna.html')

@app.route('/koncerty')
def koncerty():
    return render_template('koncerty.html')

@app.route('/bilety')
def bilety():
    return render_template('bilety.html')

@app.route('/ustawienia')
def ustawienia():
    return render_template('ustawienia.html')

@app.route("/login",methods = ['POST'])
def login():
    username = request.form.get('username') or ''
    password = request.form.get('password') or ''
    if hmac.compare_digest(username, Config.USERNAME or '') and hmac.compare_digest(password, Config.PASSWORD or ''):
        session['logged'] = True
        return redirect(url_for('strona_glowna'))
    else:
        return jsonify({'result': 'ERROR', 'message': 'Wrong email or password'}),401
        

# submitowanie danych do serwera
@app.route('/submit_koncerty',methods=['POST'])
def approute_koncerty():
    try:
        czas = request.form['czas']
        nazwa = request.form['nazwa']
        zespol = request.form['zespol']
        opis = request.form['opis']
        ilosc_biletow = request.form['ilosc_biletow']

        polaczenie,kursor = postgres()
        id_koncertu = odbieranie.getIdConcert(kursor)
        edycja.insert(kursor,'Koncerty',id_koncertu,czas,nazwa,zespol,opis,ilosc_biletow)
        polaczenie.commit()
        kursor.close()
        polaczenie.close()

        return redirect(url_for('koncerty'))
    except:
        return "niepoprawne dane"


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