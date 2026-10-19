### Step By Step

## Fase 1: Setup dell'ambiente (Versione 1.0.1)
Per prima cosa, dobbiamo creare la situazione "di partenza".

Crea il modulo: Nella tua cartella degli addons, crea test_migration.

Manifest (__manifest__.py):
```bash
Python
{
    'name': 'Test Migration',
    'version': '17.0.1.0.1', # Versione iniziale
    'depends': ['base'],
    'data': [],
    'installable': True,
}
```

Modello (models/test_model.py):
```bash
Python
from odoo import models, fields

class VecchiaTabella(models.Model):
    _name = 'test.vecchia_tabella' # Nome iniziale
    _description = 'Tabella Originale'

    name = fields.Char(string="Nome")
```
Avvia e Installa:

Avvia il container: docker-compose up -d

Installa il modulo: vai nell'interfaccia di Odoo e installa test_migration.

Crea i Dati: Vai in Impostazioni > Tecnico > Modelli, cerca test.vecchia_tabella e crea 2 o 3 record (es. "Dato Test 1", "Dato Test 2").

## Fase 2: Preparazione alla migrazione (Versione 1.1.0)
Ora simuliamo il cambiamento del codice. Non aggiornare ancora il modulo su Docker!

Modifica il Manifest: Cambia la versione in '17.0.1.0.1'.

Rinomina il Modello: Nel file Python, cambia _name in 'test.nuova_tabella'.

Crea la cartella di migrazione:
La struttura deve essere: test_migration/migrations/17.0.1.0.1/pre-migrate.py.
Nota: Il nome della cartella deve corrispondere esattamente alla nuova versione nel manifest.

Scrivi lo script di migrazione: Incolla questo nel file pre-migrate.py:

Python
```
# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    # Trasformiamo i nomi tecnici di Odoo in nomi di tabelle Postgres (sostituendo il punto con l'underscore)
    old_table = 'test_vecchia_tabella'
    new_table = 'test_nuova_tabella'

    # 1. Rinominiamo la tabella fisica nel DB
    _logger.info(f"Rinomino tabella da {old_table} a {new_table}")
    cr.execute(f"ALTER TABLE {old_table} RENAME TO {new_table}")

    # 2. Aggiorniamo i riferimenti interni di Odoo
    # Questo evita che Odoo pensi che il vecchio modello sia sparito
    cr.execute("UPDATE ir_model SET model = %s WHERE model = %s", (new_table.replace('_', '.'), old_table.replace('_', '.')))
    cr.execute("UPDATE ir_model_data SET model = %s WHERE model = %s", (new_table.replace('_', '.'), old_table.replace('_', '.')))
```
Fase 3: Esecuzione su Docker
Per far sì che Odoo veda i nuovi file e avvii la migrazione, segui questi comandi dal terminale:

Riavvia il container (per fargli leggere i nuovi file Python):

Bash:
```
docker-compose restart odoo
```
Lancia l'aggiornamento via riga di comando (è il modo più pulito per vedere i log):

Bash:
```
docker exec -u 0 -it nome_del_tuo_container_odoo odoo -u test_migration -d nome_del_tuo_db --stop-after-init
-u
```
: aggiorna il modulo.

-d: specifica il database.

--stop-after-init: chiude Odoo dopo aver finito l'aggiornamento.

Fase 4: Verifica
Accedi nuovamente a Odoo.

Vai su Impostazioni > Tecnico > Modelli.

Cerca test.nuova_tabella.

Il momento della verità: Controlla i record. Se tutto è andato bene, troverai i dati che avevi inserito nella "Vecchia Tabella" ora presenti nella "Nuova Tabella".

## PS:  ho creato la view per la creazione di dati e verifica in modo piu semplice 

