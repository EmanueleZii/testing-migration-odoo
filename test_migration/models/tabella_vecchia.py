from odoo import models, fields

class VecchiaTabella(models.Model):
    _name = 'test.vecchia_tabella' # Nome iniziale
    _description = 'Tabella Originale'

    name = fields.Char(string="Nome")