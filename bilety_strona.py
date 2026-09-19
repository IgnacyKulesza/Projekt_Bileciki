from flask import Flask,render_template,request,redirect,url_for
import psycopg
import edycja_danych as edycja
import odbieranie_danych as odbieranie
from config import Config

def postgres():

    polaczenie=psycopg.connect(
        host=Config.DATABASE_HOST,
        port=Config.DATABASE_PORT,
        database= Config.DATABASE_NAME,
        user=Config.DATABASE_USER,
        password=Config.DATABASE_PASSWORD
    )

    kursor=polaczenie.cursor()
    return polaczenie,kursor


app = Flask(__name__, template_folder="HTML", static_folder="HTML/static")


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

@app.route("/login")
def login():
    if(login == login and haslo == "password1"):
        login

# submitowanie danych do serwera
@app.route('/submit_koncerty',methods=['POST'])
def approute_koncerty():
    id_koncertu = request.form['id_koncertu']
    czas = request.form['czas']
    nazwa = request.form['nazwa']
    zespol = request.form['zespol']
    opis = request.form['opis']

    polaczenie,kursor = postgres()
    edycja.insert(kursor,"Bilety",id_koncertu,czas,nazwa,zespol,opis)
    polaczenie.commit()
    kursor.close()
    polaczenie.close()

    return redirect(url_for('koncerty'))


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