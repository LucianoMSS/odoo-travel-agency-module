from odoo import models, fields, api

class TravelAgencyCollection(models.Model):
    _name = 'travel.agency.collection'
    _description = 'Payment Collection Report'
    _order = 'date desc, id desc'

    date = fields.Date(string='Payment Date', default=fields.Date.context_today)
    payment_method = fields.Selection([
        ('transf', 'Wire Transfer'),
        ('efectivo', 'Cash'),
        ('tarjeta', 'Credit/Debit Card'),
        ('traspaso', 'Internal Transfer'),
        ('cheque', 'Check'),
        ('otro', 'Other')
    ], string='Payment Method', default='transf')
    
    bank_id = fields.Many2one('account.journal', string='Bank Journal', domain=[('type', '=', 'bank')])
    
    dk = fields.Char(string='DK Reference', help="Client / Trip Reference Code")
    partner_id = fields.Many2one('res.partner', string='Client', compute='_compute_references', store=True, readonly=False)
    viaje_id = fields.Many2one('travel.agency.trip', string='Trip', compute='_compute_references', store=True, readonly=False)
    
    rc_number = fields.Char(string='Receipt Number (RC)', help="Receipt Sequential Number")
    document_ref = fields.Char(string='Document Folio', help="Invoice / Document Number")
    reference = fields.Char(string='Voucher Reference')
    
    amount_untaxed_0 = fields.Float(string='0% Tax-Exempt Base')
    amount_traspaso = fields.Float(string='Transfer Amount')
    amount_untaxed_16 = fields.Float(string='16% Taxable Base')
    
    amount_tax_16 = fields.Float(string='VAT 16%', compute='_compute_amounts', store=True)
    amount_cobranza = fields.Float(string='Total Collection', compute='_compute_amounts', store=True)
    
    bank_deposit = fields.Float(string='Bank Deposit Amount')
    bank_movement_id = fields.Char(string='Bank Batch ID', help="ID used to group multiple entries into a single deposit")
    
    notes = fields.Text(string='Notes')

    @api.depends('dk')
    def _compute_references(self):
        for record in self:
            if record.dk:
                dk_upper = record.dk.strip().upper()
                # Find Partner by DK / reference code
                partner = self.env['res.partner'].search([('ref', '=', dk_upper)], limit=1)
                if partner:
                    record.partner_id = partner
                # Find Trip by DK reference code
                viaje = self.env['travel.agency.trip'].search([('dk', '=', dk_upper)], limit=1)
                if viaje:
                    record.viaje_id = viaje

    @api.depends('amount_untaxed_0', 'amount_traspaso', 'amount_untaxed_16')
    def _compute_amounts(self):
        for record in self:
            # VAT tax is 16% of taxable base
            record.amount_tax_16 = record.amount_untaxed_16 * 0.16
            # Total collection includes tax-free base, transfers, taxable base, and VAT
            record.amount_cobranza = (
                record.amount_untaxed_0 + 
                record.amount_traspaso + 
                record.amount_untaxed_16 + 
                record.amount_tax_16
            )

    def action_generate_payment(self):
        """Generates an Odoo native account.payment record from this collection line."""
        for record in self:
            if not record.partner_id or record.amount_cobranza <= 0:
                continue
            
            payment_vals = {
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'partner_id': record.partner_id.id,
                'amount': record.amount_cobranza,
                'date': record.date,
                'journal_id': record.bank_id.id or self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
                'ref': f"Collection {record.rc_number or ''} {record.document_ref or ''}".strip(),
                'memo': f"DK: {record.dk}",
            }
            self.env['account.payment'].create(payment_vals)
