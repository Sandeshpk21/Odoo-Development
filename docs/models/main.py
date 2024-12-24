# from odoo import models, fields, api

# class Main(models.Model):    
#     _name = 'docs.main'
#     _description = 'Document Files'

#     file_name = fields.Char(string='File Name', required=True)
#     description = fields.Char(string='Description', required=True)
#     author = fields.Many2one('res.users', string='File Author', required=True)
#     creation_date = fields.Datetime(string='Creation Date', required=True, default=fields.Datetime.now)
#     modification_date = fields.Datetime(string='Modification Date', compute='_compute_modification_date', store=True)
#     version = fields.Integer(string='Version', required=True, default=1)
#     file = fields.Binary(string='Upload File', required=True, attachment=True)
#     file_name = fields.Char(string='File Name')

#     folder_id = fields.Many2one('docs.folder', string='Folder', ondelete='cascade', required=True)

#     @api.depends('file', 'description', 'author', 'file_name')
#     def _compute_modification_date(self):
#         for record in self:
#             record.modification_date = fields.Datetime.now()

#     @api.onchange('file')
#     def _onchange_file(self):
#         for record in self:
#             if record.file:
#                 record.version += 1


from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Main(models.Model):
    _name = 'docs.main'
    _description = 'Document Files'

    file_name = fields.Char(string='Name')
    description = fields.Char(string='Description', required=False)
    author = fields.Many2one('res.users', string='File Author', required=False)
    folder_id = fields.Many2one('docs.folder', string='Folder', ondelete='cascade')
    creation_date = fields.Datetime(string='Creation Date', default=fields.Datetime.now)
    modification_date = fields.Datetime(string='Modification Date', compute='_compute_modification_date', store=True)
    version = fields.Integer(string='Version', default=1)
    file = fields.Binary(string='Upload File', required=True, attachment=True)
    

    @api.depends('file', 'description', 'author', 'file_name')
    def _compute_modification_date(self):
        for record in self:
            record.modification_date = fields.Datetime.now()

    @api.onchange('file')
    def _onchange_file(self):
        for record in self:
            if record.file:
                record.version += 1

    @api.model
    def create(self, vals):
        record = super(Main, self).create(vals)
        # Auto-fill the author field if not provided
           
        record.author = self.env.user.id
        record.creation_date = fields.Datetime.now()
        record.modification_date = fields.Datetime.now()
        record.file = vals.get('file')
        record.folder_id = vals.get('folder_id')
        
        return record

        
