DROP TABLE IF EXISTS Bilety;
DROP TABLE IF EXISTS Koncerty;

CREATE TABLE Koncerty
(
    id_koncertu INTEGER SERIAL PRIMARY KEY,
    czas TIMESTAMP,
    nazwa VARCHAR(31),
    zespol VARCHAR(127),
    opis VARCHAR(513),
	ilosc_biletow INTEGER
);

CREATE TABLE Bilety
(
    id_biletu VARCHAR PRIMARY KEY,
    czy_zeskanowane BOOL,
    imie VARCHAR(31),
    nazwisko VARCHAR(63),
    id_koncertu INTEGER REFERENCES Koncerty(id_koncertu)
);


INSERT INTO Koncerty (id_koncertu, czas, nazwa, zespol, opis)
VALUES
(1, '2026-10-10 19:00:00', 'Jesienny Koncert', 'Daria Zawiałow',
 'Koncert promujący najnowszą trasę koncertową artystki.'),

(2, '2026-10-18 20:00:00', 'Nocne Granie', 'Kwiat Jabłoni',
 'Wieczorny koncert zespołu w ramach jesiennej trasy.'),

(3, '2026-11-07 19:30:00', 'Live 2026', 'Mrozu',
 'Koncert z największymi przebojami oraz utworami z najnowszej płyty.'),

(4, '2026-11-21 18:00:00', 'Muzyka na Żywo', 'Vito Bambino',
 'Specjalny koncert klubowy z muzyką na żywo.'),

(5, '2026-12-05 20:00:00', 'Winter Tour', 'Sanah',
 'Zimowa trasa koncertowa z największymi hitami artystki.'),

(6, '2026-12-19 19:00:00', 'Rock Night', 'Dżem',
 'Wieczór pełen klasycznych rockowych utworów zespołu.'),

(7, '2027-01-16 20:00:00', 'Nowy Rok Live', 'Lady Pank',
 'Koncert noworoczny z największymi przebojami zespołu.');


INSERT INTO Bilety (id_biletu, czy_zeskanowane, imie, nazwisko, id_koncertu)
VALUES
('BIL001', TRUE,  'Jan',     'Kowalski', 1),
('BIL002', FALSE, 'Anna',    'Nowak',    1),
('BIL003', TRUE,  'Piotr',   'Wiśniewski', 1),

('BIL004', FALSE, 'Michał',  'Wójcik',   2),
('BIL005', TRUE,  'Julia',   'Kamińska', 2),
('BIL006', FALSE, 'Adam',    'Lewandowski', 2),

('BIL007', TRUE,  'Kacper',  'Zieliński', 3),
('BIL008', FALSE, 'Oliwia',  'Szymańska', 3),
('BIL009', FALSE, 'Jakub',   'Woźniak',   3),

('BIL010', TRUE,  'Zuzanna', 'Kozłowska', 4),
('BIL011', FALSE, 'Mateusz', 'Jankowski', 4),

('BIL012', FALSE, 'Amelia',  'Mazur',     5),
('BIL013', TRUE,  'Antoni',  'Krawczyk',  5),
('BIL014', FALSE, 'Wiktoria','Piotrowska',5),

('BIL015', TRUE,  'Filip',   'Grabowski', 6),
('BIL016', FALSE, 'Natalia', 'Pawłowska', 6),

('BIL017', FALSE, 'Szymon',  'Michalski', 7),
('BIL018', TRUE,  'Maja',    'Król',      7);