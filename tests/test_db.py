from odbieranie_danych import getConcertCount
from unittest.mock import MagicMock

def test_getConcertCount():
    kursor = MagicMock()
    kursor.fetchone.return_value = (6,)
    assert getConcertCount(kursor) == 6
        # testowana funkcja ^^       ^^^ oczekiwany wynik
        # pytest szuka assertów


