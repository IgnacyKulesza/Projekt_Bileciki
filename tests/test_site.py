from pathlib import Path
import pytest
import re
import main as mainmodule

endpoints = ["/","/strona-glowna","/koncerty","/bilety","/ustawienia"]

forms = {"/koncerty": ("/submit_koncerty",['czas','nazwa','zespol','opis','ilosc_biletow']),
         "/bilety": ("/submit_bilety",['imie','nazwisko','id_koncertu']),
         "/": ("/login",['username','password'])}

@pytest.fixture
def client():
    mainmodule.app.config["TESTING"] = True
    return mainmodule.app.test_client()

@pytest.fixture
def logged(client):
    with client.session_transaction() as session:
        session["logged"] = True
    
    return client


def html(client, address):
    return client.get(address).get_data(as_text = True)

@pytest.mark.parametrize("address",endpoints)
def test_do_pages_open(logged, address):
    response = logged.get(address)
    assert response.status_code == 200
    assert response.content_type.startswith() == 'text/html'

@pytest.mark.parametrize("address",endpoints)
def test_is_complete_HTML(logged, address):
    text = html(logged,address).lower()
    assert "<html" in text and "</html>" in text


