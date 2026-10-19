from odoo import models, fields, api

class TestNuovo(models.Model):
    _name = 'test.nuovo'
    _description = "Test Nuovo"
    name =  fields.Char('Nome')