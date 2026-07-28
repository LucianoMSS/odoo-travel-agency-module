from odoo import models, fields, api

class TravelAgencyTrip(models.Model):
    _name = 'travel.agency.trip'
    _description = 'Travel Agency Trip'
    _order = 'date_start desc'

    name = fields.Char(string='Trip Name', required=True)
    pnr = fields.Char(string='PNR', help="Record Locator / Reservation Code")
    partner_id = fields.Many2one('res.partner', string='Client')
    dk = fields.Char(string='DK Reference', help="Client / Account Reference")
    
    # External Integration / AppSheet Fields
    appsheet_id = fields.Char(string='External App ID', copy=False)
    solicitud_asociada = fields.Char(string='Associated Request')
    link_costos = fields.Char(string='Cost Sheet URL')
    asesor = fields.Char(string='Travel Agent')
    categoria = fields.Char(string='Category')
    especialidad = fields.Char(string='Specialty')
    num_pax = fields.Integer(string='Passenger Count (PAX)')
    balance_appsheet = fields.Float(string='External Balance')
    state_appsheet = fields.Char(string='External State')
    destination_desc = fields.Char(string='Destination')
    travelers_desc = fields.Text(string='Passenger Names')
    
    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Completed'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft')
    
    invoice_ids = fields.One2many('account.move', 'viaje_id', string='Invoices & Bills')

    # Computed fields for margin & profitability
    total_income = fields.Float(string='Total Revenue', compute='_compute_margin', store=True)
    total_cost = fields.Float(string='Total Costs', compute='_compute_margin', store=True)
    total_margin = fields.Float(string='Net Margin', compute='_compute_margin', store=True)

    @api.depends('invoice_ids', 'invoice_ids.amount_untaxed', 'invoice_ids.move_type', 'invoice_ids.state')
    def _compute_margin(self):
        for record in self:
            incomes = record.invoice_ids.filtered(lambda m: m.move_type == 'out_invoice' and m.state == 'posted')
            costs = record.invoice_ids.filtered(lambda m: m.move_type == 'in_invoice' and m.state == 'posted')
            
            record.total_income = sum(incomes.mapped('amount_untaxed'))
            record.total_cost = sum(costs.mapped('amount_untaxed'))
            record.total_margin = record.total_income - record.total_cost
