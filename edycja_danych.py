import psycopg
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


def insert(kursor,tabela,argument1,argument2,argument3,argument4,argument5):
    if tabela in ('Koncery', 'Bilety'):
        kursor.execute(f'INSERT INTO {tabela}'
                        'VALUES(DEFAULT,%s,%s,%s,%s,%s))',(argument1,argument2,argument3,argument4,argument5))
        print(f"dodano {argument1}, {argument2}, {argument3}, {argument4}, {argument5}")

def delete(kursor,tabela,usuwane):
    if tabela=="koncerty":
        kursor.execute(f'DELETE FROM {tabela} WHERE id_koncertu = %s',usuwane)
    elif tabela=="bilety":
        kursor.execute(f'DELETE FROM {tabela} WHERE id_biletu = %s',usuwane)

    

def edit(kursor,tabela,kolumna,zedytowane,idelementu):
    if tabela == 'Koncerty':
        kursor.execute('UPDATE Koncerty SET '+kolumna+' = %s WHERE id_koncertu = %s',(zedytowane,idelementu))
    elif tabela == 'Bilety':
        kursor.execute('UPDATE Bilety SET '+kolumna+' = %s WHERE id_biletu = %s',(zedytowane,idelementu))
    


polaczenie,kursor=postgres()
polaczenie.commit()
kursor.close()
polaczenie.close()
