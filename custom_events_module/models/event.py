import base64
from datetime import datetime
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class Event(models.Model):
    _name = 'custom.event'
    _description = 'Custom Event'

    name = fields.Char(string='Event Name', required=True)
    description = fields.Text(string='Description')
    date_begin = fields.Datetime(string='Start Date and Time', required=True)
    date_end = fields.Datetime(string='End Date and Time', required=True)
    location = fields.Char(string='Location',required=True,compute='_compute_location',readonly=False, store=True)
    is_online = fields.Boolean(string='online Event',required=True, default=False, store=True)
    online_link = fields.Char(string='online Link')
    organizer_id = fields.Many2one('res.users', string='Organizer')
    # participants_user_ids = fields.Many2many('res.users', string='Participants')
    # limit_participants = fields.Boolean(string='Limit Participants', default=False, required=True,compute='_compute_seats', store=True,precompute=True, readonly=False)
    seats_available = fields.Integer(string='Available Seats', compute='_compute_seats', store=True, default=0)
    # price = fields.Float(string='Price')

    registration_ids = fields.One2many('custom.event.registration', 'event_id', string='Registrations')

    ticket_ids = fields.One2many('custom.event.ticket', 'event_id', string='Tickets')
    event_image = fields.Image('Event Poster')   
    
    @api.depends('ticket_ids.available_quantity')
    def _compute_seats(self):
        sum = 0
        for event in self:
            if event.ticket_ids:
                for ticket in event.ticket_ids:
                    sum = sum + ticket.available_quantity
                event.seats_available =sum



    @api.depends('is_online')
    def _compute_location(self):
        for event in self:
            event.location = 'online_event' if event.is_online else event.location

    @api.model
    def action_send_email_to_internal_user(self,temp):
        # _logger.info('temp: %s', temp)
        # Logic to create a registration record
        email_list = self.participants_user_ids
        _logger.info('\n\n\n\nemail_list: %s', email_list)
        for email in email_list:
            _logger.info('\nemail in for loop: %s', email)
            mail_values = {
                'subject': f"Event Registration Confirmation: {self.name}",
                'body_html': f"""
                    <p> Hello Internal User,</p>
                    <p>Hello {'Guest'},</p>
                    <p>Thank you for registering for the event <strong>{self.name}</strong>.</p>
                    <p><strong>Event Name:</strong> {self.name}</p>
                    <p><strong>Date:</strong> {self.date_begin('%B %d, %Y')} to {self.date_end('%B %d, %Y')}</p>
                    <p><strong>Location:</strong> {self.location if self.location else 'Online'}</p>
                    <p>We look forward to seeing you at the event.</p>
                    <p>Thank you,</p>
                    <p>{self.organizer_id.name or 'The Event Team'}</p>
                """,
                'email_to': email,  # Sending to the registered user's email
                'email_from': self.organizer_id.email,  # Default to event organizer or responsible person
                }

            self.env['mail.mail'].create(mail_values).send()

    @api.model
    def action_custom_event(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Custom Events',
            'res_model': 'custom.event',
            'view_mode': 'tree,form',
            'target': 'current',  # Use 'current' or 'inline' based on your requirement
        }
    

    
    
    
