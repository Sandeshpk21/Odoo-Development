# from odoo import models, fields

# class Folder(models.Model):
#     _name = 'docs.folder'
#     _description = 'Folder Hierarchy'

#     name = fields.Char(string='Folder Name', required=True)
#     parent_id = fields.Many2one('docs.folder', string='Parent Folder', ondelete='cascade')
#     child_ids = fields.One2many('docs.folder', 'parent_id', string='Subfolders')
#     file_ids = fields.One2many('docs.main', 'folder_id', string='Files in Folder')

#     def get_folder_contents(self):
#         """Fetch subfolders and files for a given folder"""
#         self.ensure_one()
#         subfolders = self.child_ids
#         files = self.file_ids
#         return {
#             'subfolders': subfolders,
#             'files': files
#         }

from odoo import models, fields, api


class Folder(models.Model):
    _name = 'docs.folder'
    _description = 'Folder Hierarchy'

    name = fields.Char('Folder Name', required=True)
    parent_id = fields.Many2one('docs.folder', string='Parent Folder', ondelete='cascade')
    child_ids = fields.One2many('docs.folder', 'parent_id', string='Subfolders')
    file_ids = fields.One2many('docs.main', 'folder_id', string='Files')
    is_root = fields.Boolean(string='Is Root Folder', default=False)

    @api.depends('parent_id')
    def get_breadcrumb(self):
        """Get the breadcrumb path for navigation."""
        breadcrumb = []
        folder = self
        while folder:
            breadcrumb.append(folder)
            folder = folder.parent_id
        return breadcrumb[::-1]  # Reverse to get root-to-current folder path
