# # # -*- coding: utf-8 -*-

# from odoo import http
# from odoo.http import request

# class EventRegistration(http.Controller):

#     @http.route('/custom_event_list', type='http', auth="public", website=True)
#     def event_list(self, **kwargs):
#         events = request.env['custom.event'].sudo().search([])
#         return request.render("custom_events_module.event_listing_page", {'events': events})

#     @http.route('/custom_event_detail/<int:event_id>', type='http', auth="public", website=True)
#     def event_detail(self, event_id, **kwargs):
#         event = request.env['custom.event'].sudo().browse(event_id)
#         if not event.exists():
#             return request.not_found()
#         return request.render("custom_events_module.event_detail_page", {'event': event})

#     @http.route('/custom_event_registration/<int:event_id>', type='http', auth="public", website=True)
#     def event_registration(self, event_id, **kwargs):
#         event = request.env['custom.event'].sudo().browse(event_id)
#         tickets = request.env['custom.event.ticket'].sudo().search([('event_id', '=', event_id)])
#         return request.render("custom_events_module.event_website_registration", {
#             'event': event,
#             'tickets': tickets,
#         })

    

#     @http.route(['/create/registration'], type='http', auth="public", website=True, csrf=True)
#     def create_registration(self, **post):
#         event_id = int(post.get('event_id'))
#         ticket_id = int(post.get('ticket_id'))
        
#         # Get the selected ticket
#         ticket = request.env['custom.ticket'].sudo().browse(ticket_id)
        
#         # Check if ticket price is greater than zero
#         if ticket.price > 0:
#             return request.redirect('/event_payment/%d/%d' % (event_id, ticket_id))
        
#         # Otherwise, confirm registration and show thanks page
#         # Assuming registration logic is here
        
#         return request.redirect('/Registration-thank-you')

#     @http.route(['/event_payment/<int:event_id>/<int:ticket_id>'], type='http', auth="public", website=True)
#     def event_payment(self, event_id, ticket_id, **kwargs):
#         event = request.env['custom.event'].sudo().browse(event_id)
#         ticket = request.env['custom.ticket'].sudo().browse(ticket_id)
        
#         return request.render('custom_events_module.event_payment_page', {
#             'event': event,
#             'ticket': ticket
#         })

# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class EventRegistration(http.Controller):

    @http.route('/custom_event_list', type='http', auth="public", website=True)
    def event_list(self, **kwargs):
        events = request.env['custom.event'].sudo().search([])
        return request.render("custom_events_module.event_listing_page", {'events': events})

    @http.route('/custom_event_detail/<int:event_id>', type='http', auth="public", website=True)
    def event_detail(self, event_id, **kwargs):
        event = request.env['custom.event'].sudo().browse(event_id)
        if not event.exists():
            return request.not_found()
        return request.render("custom_events_module.event_detail_page", {'event': event})

    @http.route('/custom_event_registration/<int:event_id>', type='http', auth="public", website=True)
    def event_registration(self, event_id, **kwargs):
        event = request.env['custom.event'].sudo().browse(event_id)
        tickets = request.env['custom.event.ticket'].sudo().search([('event_id', '=', event_id)])
        return request.render("custom_events_module.event_website_registration", {
            'event': event,
            'tickets': tickets,
        })
        

    @http.route(['/create/registration'], type='http', auth="public", website=True, csrf=True)
    def create_registration(self, **post):
        event_id = int(post.get('event_id'))
        ticket_id = int(post.get('ticket_id'))
        
        # Get the selected ticket and check if it exists
        ticket = request.env['custom.event.ticket'].sudo().browse(ticket_id)
        if not ticket.exists():
            return request.not_found()
        
        # Check if ticket price is greater than zero
        if ticket.price > 0:
            return request.redirect('/event_payment/%d/%d' % (event_id, ticket_id))
        
        request.env['custom.event.registration'].sudo().create({
            'name': post.get('name'),
            'email': post.get('email'),
            'event_id': int(post.get('event_id')),
            'ticket_id': int(post.get('ticket_id')),
        })
        
        # Confirm registration (add registration creation logic here if needed)
        # Redirect to the thank-you page
        return request.redirect('/Registration-thank-you')

    @http.route(['/event_payment/<int:event_id>/<int:ticket_id>'], type='http', auth="public", website=True)
    def event_payment(self, event_id, ticket_id, **kwargs):
        event = request.env['custom.event'].sudo().browse(event_id)
        ticket = request.env['custom.event.ticket'].sudo().browse(ticket_id)
        if not event.exists() or not ticket.exists():
            return request.not_found()
        
        return request.render('custom_events_module.event_payment_page', {
            'event': event,
            'ticket': ticket
        })
    
