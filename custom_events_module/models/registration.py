from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
from pytz import timezone # type: ignore
from datetime import datetime
import base64

_logger = logging.getLogger(__name__)


class EventRegistration(models.Model):
    _name = 'custom.event.registration'
    _description = 'Event Registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Attendee Name', required=True)
    email = fields.Char(string='Email', required=True)
    event_id = fields.Many2one('custom.event', string='Event', required=True)
    state = fields.Selection([('Registred', 'Registred'),('Canceled', 'Canceled')], string='State', default=None, readonly=True)
    ticket_id = fields.Many2one('custom.event.ticket', string='Ticket Type', required=True, domain="[('event_id', '=', event_id)]")

    payment_status = fields.Selection(
        [('pending', 'Pending'), ('paid', 'Paid'), ('cancelled', 'Cancelled')],
        default='pending', string='Payment Status'
    )
    payment_transaction_id = fields.Many2one(
        'payment.transaction', string='Payment Transaction'
    )

    # Method to create and initiate payment transaction
    def initiate_payment_transaction(self):
        if self.ticket_id.price > 0:
            # Create payment transaction
            transaction = self.env['payment.transaction'].create({
                'amount': self.ticket_id.price,
                'currency_id': self.env.ref('base.INR').id,
                'acquirer_id': self.env.ref('payment_acquirer_your_provider').id,  # Replace with your acquirer XML ID
                'reference': f'{self.id}-event-registration',
                'partner_id': self.env.user.partner_id.id,
            })
            self.payment_transaction_id = transaction
            return transaction._get_processing_url()

    @api.depends('event_id')
    def _onchange_event_id(self):
        for record in self:
            record.event_id.ensure_one()
            record.ticket_id = False
            return{'domain': {'ticket_id': [('event_id', '=', record.event_id.id)]}}

    @api.model
    def create(self, vals):
        # Create the registration record
        record = super(EventRegistration, self).create(vals)

        if record.state == 'Registred':
            raise ValidationError("Registration is already registred.")
        
        record.state = 'Registred' 
        
        if record.event_id.ticket_ids:
            for ticket in record.event_id.ticket_ids:
                if ticket.id == record.ticket_id.id:
                    if ticket.available_quantity > 0:
                        ticket.available_quantity -= 1
                        _logger.info(f'Ticket {ticket.name} sold. {ticket.available_quantity} left.')
                    else:
                        _logger.warning(f'No available tickets for {ticket.name}')
                        raise ValidationError(f'All tickets {ticket.name} sold. {ticket.available_quantity} left.')
        
        # If there's a ticket price, initiate the payment
        if record.ticket_id.price > 0:
            payment_url = record.initiate_payment_transaction()
            return {
                'type': 'ir.actions.act_url',
                'url': payment_url,
                'target': 'self',
            }

        # Generate the iCalendar content
        event_start = record.event_id.date_begin
        event_end = record.event_id.date_end

        # Generate the .ics file content
        ics_content = (
            "BEGIN:VCALENDAR\n"
            "VERSION:2.0\n"
            "PRODID:-//Your Organization//Your App Name//EN\n"
            "METHOD:PUBLISH\n"
            "BEGIN:VEVENT\n"
            f"UID:{record.id}@yourdomain.com\n"
            f"DTSTAMP:{datetime.now(timezone('UTC')).strftime('%Y%m%dT%H%M%SZ')}\n"
            f"DTSTART:{event_start.strftime('%Y%m%dT%H%M%SZ')}\n"
            f"DTEND:{event_end.strftime('%Y%m%dT%H%M%SZ')}\n"
            f"SUMMARY:{record.event_id.name}\n"
            f"DESCRIPTION:Join us for the event {record.event_id.name}.\n"
            f"LOCATION:{record.event_id.location or 'Online'}\n"
            "STATUS:CONFIRMED\n"
            "END:VEVENT\n"
            "END:VCALENDAR"
        )

        # Encode the .ics content to base64
        ics_base64 = base64.b64encode(ics_content.encode('utf-8'))

        # Create the .ics attachment in Odoo
        
        mail_values = {
            'subject': f"Event Registration Confirmation: {record.event_id.name}",
            'body_html': f"""
                <p>Hello {record.name or 'Guest'},</p>
                <p>Thank you for registering for the event <strong>{record.event_id.name}</strong>.</p>
                <p><strong>Event Name:</strong> {record.event_id.name}</p>
                <p><strong>Date:</strong> {event_start.strftime('%B %d, %Y')} to {event_end.strftime('%B %d, %Y')}</p>
                <p><strong>Location:</strong> {record.event_id.location or 'Online'}</p>

                <p>We look forward to seeing you at the event.</p>
                <p>{record.event_id.organizer_id.name or 'The Event Team'}</p>
            """,
            'email_to': record.email,
            'email_from': record.event_id.organizer_id.email or 'noreply@example.com',
            'attachment_ids': [(0, 0, {
                'name': f"{record.event_id.name}.ics",
                'type': 'binary',
                'datas': ics_base64,
                'mimetype': 'text/calendar',
            })]
        }

        self.env['mail.mail'].create(mail_values).send()

        return record
    
    # Method to handle successful payment
    def process_payment_success(self):
        self.payment_status = 'paid'
        _logger.info(f'Payment successful for registration {self.id}.')

    def register(self):
        self.state = 'Registred'
        self.env.cr.commit()
        return True


    def cancel_registration(self):
        # Check if the registration is already cancelled
        if self.state == 'Canceled':
            raise ValidationError("Registration is already cancelled.")

        # Update the registration state to 'Canceled'
        self.state = 'Canceled'

        # If the event has tickets, increment the available quantity of the ticket
        if self.event_id.ticket_ids:
            for ticket in self.event_id.ticket_ids:
                if ticket.id == self.ticket_id.id:
                    ticket.available_quantity += 1

        # Send a cancellation email to the registered user
        mail_values = {
            'subject': f"Event Registration Cancellation: {self.event_id.name}",
            'body_html': f"""
                <p>Hello {self.name or 'Guest'},</p>
                <p>Your registration for the event <strong>{self.event_id.name}</strong> has been cancelled.</p>
                <p><strong>Event Name:</strong> {self.event_id.name}</p>
                <p><strong>Date:</strong> {self.event_id.date_begin.strftime('%B %d, %Y')} to {self.event_id.date_end.strftime('%B %d, %Y')}</p>
                <p><strong>Location:</strong> {self.event_id.location if self.event_id.location else 'Online'}</p>
                <p>Thank you,</p>
                <p>{self.event_id.organizer_id.name or 'The Event Team'}</p>
            """,
            'email_to': self.email,  # Sending to the registered user's email
            'email_from': self.event_id.organizer_id.email,  # Default to event organizer or responsible person
        }
        # self.env['mail.mail'].create(mail_values).send()