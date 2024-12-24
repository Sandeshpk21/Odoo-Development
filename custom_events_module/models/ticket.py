from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class EventTicket(models.Model):
    _name = 'custom.event.ticket'
    _description = 'Event Ticket'

    name = fields.Char(string='Ticket Name', required=True)
    event_id = fields.Many2one('custom.event', string='Event', required=True, ondelete='cascade')
    price = fields.Float(string='Price', required=True)
    available_quantity = fields.Integer(string='Available Tickets', required=True)
    sold_quantity = fields.Integer(string='Sold Tickets', compute='_compute_sold_quantity', store=True)

    @api.depends('event_id', 'event_id.registration_ids')
    def _compute_sold_quantity(self):
        # _logger.info('\nAviailabel quantity: %s', self.available_quantity)
        # _logger.info('Number of registred attendies: %s',len(self.event_id.registration_ids))

        for ticket in self:
            # _logger.info('\nNumber of registred attendies inside for loop: %s',len(ticket.event_id.registration_ids))
            # ticket.sold_quantity = len(ticket.event_id.registration_ids)
               # _logger.info('\nNumber of registred attendies inside for loop: %s',len(ticket.event_id.registration_ids))
            count = 0
            for temp in ticket.event_id.registration_ids:
                if ticket.id == temp.ticket_id.id:
                    count += 1
                    
            ticket.sold_quantity = count
