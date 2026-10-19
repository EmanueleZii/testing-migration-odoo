from odoo import models, fields, api

class TestVecchio(models.Model):
    _name = 'test.vecchio'
    _description = "Test Vecchio"
    name =  fields.Char('Nome')