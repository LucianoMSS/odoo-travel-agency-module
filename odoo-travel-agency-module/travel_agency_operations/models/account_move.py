from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    viaje_id = fields.Many2one('travel.agency.trip', string='Trip', ondelete='set null')
