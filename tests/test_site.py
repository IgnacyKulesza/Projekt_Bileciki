from pathlib import Path
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch
import pytest
import re
import main as mainmodule

endpoints = ["/","/strona-glowna","/koncerty","/bilety","/ustawienia"]
protected_endpoints = [
    "/strona-glowna",
    "/koncerty",
    "/bilety",
    "/ustawienia",
]

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
    assert response.content_type.startswith("text/html")

@pytest.mark.parametrize("address",endpoints)
def test_is_complete_HTML(logged, address):
    text = html(logged,address).lower()
    assert "<html" in text and "</html>" in text

@pytest.mark.parametrize("address",protected_endpoints)
def test_pages_require_login(address,client):
    response = client.get(address)
    assert response.status_code == 400
    assert "Nie zalogowany" in response.get_data(as_text=True)

def test_login_with_wrong_password(client):
    response = client.post("/login", data = {"username": "siema.mordo@gmail.com",
                                  "password": "zle-haslo"})
    assert response.status_code == 401
    assert "Nieprawidłowy email lub hasło" in response.get_data(as_text = True)

def test_login_with_wrong_email(client):
    response = client.post("/login", data = {"username": "zly-email@gmail.com",
                                      "password": "ILoveProgramming#2026"})
    assert response.status_code == 401
    assert "Nieprawidłowy email lub hasło" in response.get_data(as_text = True)

def test_successful_login(client):
    response = client.post("/login", data = {"username": "siema.mordo@gmail.com",
                                          "password": "ILoveProgramming#2026"})
    assert response.status_code == 200


koncert_data = {
    "czas": "2027-06-15T19:00",
    "nazwa": "Test concert",
    "zespol": "Test band",
    "opis": "Concert description",
    "ilosc_biletow": "100",
}


@pytest.mark.parametrize(
    ("field", "value", "expected_message"),
    [
        ("czas", "not-a-date", "Wybierz prawidłową datę i godzinę."),
        ("nazwa", "", "Nazwa koncertu jest wymagana i może mieć maksymalnie 31 znaków."),
        ("nazwa", "x" * 32, "Nazwa koncertu jest wymagana i może mieć maksymalnie 31 znaków."),
        ("zespol", "", "Nazwa zespołu jest wymagana i może mieć maksymalnie 127 znaków."),
        ("zespol", "x" * 128, "Nazwa zespołu jest wymagana i może mieć maksymalnie 127 znaków."),
        ("opis", "", "Opis jest wymagany i może mieć maksymalnie 513 znaków."),
        ("opis", "x" * 514, "Opis jest wymagany i może mieć maksymalnie 513 znaków."),
        ("ilosc_biletow", "abc", "Podaj prawidłową liczbę biletów."),
        ("ilosc_biletow", "0", "Liczba biletów musi być większa od 0."),
        ("ilosc_biletow", "-1", "Liczba biletów musi być większa od 0."),
    ],
)
def test_approute_koncerty_rejects_invalid_data(
    client, field, value, expected_message
):
    data = {**koncert_data, field: value}

    with patch.object(mainmodule, "postgres") as postgres:
        response = client.post("/submit_koncerty", data=data)

    assert response.status_code == 400
    query = parse_qs(urlparse(response.headers["Location"]).query)
    assert query["message"] == [expected_message]
    postgres.assert_not_called()
    