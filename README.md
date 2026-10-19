### Vari test di migration di moduli per odoo che ho realizzato nel corso del tirocinio odoo developer (Python)



Step 1: Crea la cartella del modulo
Vai nella tua cartella degli addons (quella mappata nel Docker) e crea questa struttura:

Plaintext
addons/
  └── migration_test/
      ├── __init__.py
      ├── __manifest__.py
      └── models.py
Copia questi contenuti:

__init__.py:

Python
from . import models
__manifest__.py:

Python
{
    'name': 'Migration Test',
    'version': '18.0.1.0.0', # Partiamo dalla 1.0.0
    'depends': ['base'],
    'installable': True,
}
models.py:

Python
from odoo import models, fields

class TestVecchio(models.Model):
    _name = 'test.vecchio'
    name = fields.Char('Nome')
Step 2: Installa il modulo e crea un dato
Lancia Odoo e installa il modulo. Poi, dobbiamo inserire un dato nel database per vedere se "sopravvive".

Installa: docker-compose run --rm odoo odoo -d lab17 -i migration_test --stop-after-init

Inserisci un dato (usa la shell di Odoo):

Bash
docker-compose run --rm odoo odoo shell -d lab17
Una volta aperta la shell, scrivi:

Python
self.env['test.vecchio'].create({'name': 'Dato da salvare'})
self.env.cr.commit()
exit()
Step 3: Modifica il codice (Simuliamo il cambio)
Ora cambiamo il nome del modello nel codice.

Apri __manifest__.py e cambia la versione in '18.0.1.1.0'.

Apri models.py e cambia il nome del modello:

Python
class TestNuovo(models.Model): # Cambiato nome classe (opzionale)
    _name = 'test.nuovo'       # CAMBIATO IL NOME TECNICO (Fondamentale)
    name = fields.Char('Nome')
Step 4: Crea lo script di migrazione
Adesso diciamo a Odoo cosa fare quando vede il salto di versione. Crea la cartella migrations dentro il modulo.

Struttura:

Plaintext
migration_test/
  └── migrations/
      └── 18.0.1.1.0/
          └── pre-migration.py
Contenuto di pre-migration.py:

Python
from openupgradelib import openupgrade

def migrate(cr, version):
    # 1. Rinominiamo la tabella fisica nel database (SQL)
    # Da 'test_vecchio' a 'test_nuovo'
    openupgrade.rename_tables(cr, [('test_vecchio', 'test_nuovo')])

    # 2. Rinominiamo il riferimento nel sistema di Odoo
    # Da 'test.vecchio' a 'test.nuovo'
    openupgrade.rename_models(cr, [('test.vecchio', 'test.nuovo')])
Step 5: Lancia la migrazione
Esegui il comando di aggiornamento. Odoo vedrà che la versione nel DB è 1.0.0 e quella nel file è 1.1.0.

Bash
docker-compose run --rm -u root odoo bash -c "
  pip install openupgradelib --break-system-packages && \
  odoo -c /etc/odoo/odoo.conf -d lab17 -u migration_test --stop-after-init
"
Step 6: Verifica il risultato
Entra di nuovo nella shell di Odoo per vedere se il dato è passato alla nuova tabella:

Bash
docker-compose run --rm odoo odoo shell -d lab17
Scrivi nella shell:

Python
# Cerchiamo nel NUOVO modello
record = self.env['test.nuovo'].search([])
print(f"IL DATO È: {record.name}")
exit()
Se vedi stampato IL DATO È: Dato da salvare, la tua prima migrazione è riuscita!

-----------------------------------------------------------------------------------------------------------

### se si decide di installare due moduli

Se il modulo test_nuovo deve "ereditare" i dati di test_vecchio, lo script di migrazione deve gestire il passaggio di consegne.

Ecco come procedere step-by-step con i tuoi due moduli:

1. Configura le Dipendenze
Nel __manifest__.py di test_nuovo, devi aggiungere test_vecchio tra le dipendenze, così Odoo sa che deve caricarli insieme o che il nuovo dipende dal vecchio.

Python
# test_nuovo/__manifest__.py
{
    'name': 'Test Nuovo',
    'version': '18.0.1.0.0',
    'depends': ['base', 'test_vecchio'], # Importante!
    'installable': True,
}
2. Lo Script di Migrazione (pre-migration.py)
Poiché vuoi spostare i dati tra due tabelle esistenti (o che stanno per essere create), lo script deve essere dentro test_nuovo.

Percorso: test_nuovo/migrations/18.0.1.0.0/pre-migration.py

Ecco cosa scrivere per "fondere" i dati:

Python
from openupgradelib import openupgrade

def migrate(cr, version):
    old_model = 'test.vecchio'
    new_model = 'test.nuovo'
    old_table = 'test_vecchio'
    new_table = 'test_nuovo'

    # 1. SQL: Rinominiamo la tabella fisica se esiste
    if openupgrade.table_exists(cr, old_table):
        cr.execute(f"ALTER TABLE {old_table} RENAME TO {new_table}")
        print(f"--- SQL: Tabella {old_table} rinominata in {new_table}")

    # 2. SQL: Aggiorniamo i riferimenti dei modelli nel database di sistema
    # Questo sposta la proprietà dei record dal vecchio al nuovo modello
    cr.execute("""
        UPDATE ir_model_data 
        SET model = %s 
        WHERE model = %s
    """, (new_model, old_model))
    
    # 3. SQL: Aggiorniamo i riferimenti agli External ID (XML IDs)
    # Fondamentale se avevi dati caricati tramite XML
    cr.execute("""
        UPDATE ir_model_data 
        SET module = 'test_nuovo' 
        WHERE module = 'test_vecchio'
    """, )

    # 4. OpenUpgrade: Usiamo le funzioni della lib per pulire i residui
    # rename_models si occupa di aggiornare i campi Many2one che puntavano al vecchio modello
    openupgrade.rename_models(cr, [(old_model, new_model)])

    # 5. SQL Opzionale: Segnamo il vecchio modulo come da rimuovere
    cr.execute("UPDATE ir_module_module SET state='to remove' WHERE name='test_vecchio'")



3. Esegui il Test
Stato Iniziale: Installa test_vecchio e crea i dati (come abbiamo fatto prima).

Migrazione: Installa test_nuovo aggiornando anche la lista dei moduli.

Usa questo comando:

Bash
docker-compose run --rm -u root odoo bash -c "
  pip install openupgradelib --break-system-packages && \
  odoo -c /etc/odoo/odoo.conf -d lab17 -i test_nuovo -u test_nuovo --stop-after-init
"

