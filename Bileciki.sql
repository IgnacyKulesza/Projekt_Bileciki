DROP TABLE IF EXISTS Bilety;
DROP TABLE IF EXISTS Koncerty;

CREATE TABLE Koncerty
(
	id_koncertu INTEGER PRIMARY KEY,
	czas TIME,
	nazwa VARCHAR(31),
	zespol VARCHAR(127),
	opis VARCHAR(513)
);

CREATE TABLE Bilety
(
	id_biletu INTEGER PRIMARY KEY,
	czy_zeskanowane BOOL,
	imie VARCHAR(31),
	nazwisko VARCHAR(63),
	id_koncertu INTEGER REFERENCES Koncerty(id_koncertu)
);