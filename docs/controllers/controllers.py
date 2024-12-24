from odoo import http
from odoo.http import request
from werkzeug.utils import secure_filename

class DocumentController(http.Controller):

    @http.route('/documents', type='http', auth='public', website=True)
    def list_documents(self):
        folders = request.env['docs.folder'].search([('parent_id', '=', False)])
        files = request.env['docs.main'].search([('folder_id', '=', False)])
        return request.render('docs.document_listing_page', {'folders': folders, 'files': files})

    @http.route('/documents/folder/<int:folder_id>', type='http', auth='public', website=True)
    def folder_detail(self, folder_id):
        folder = request.env['docs.folder'].browse(folder_id)
        subfolders = request.env['docs.folder'].search([('parent_id', '=', folder_id)])
        files = request.env['docs.main'].search([('folder_id', '=', folder_id)])
        breadcrumb = folder.get_breadcrumb()
        return request.render('docs.folder_detail_page', {
            'folder': folder,
            'subfolders': subfolders,
            'files': files,
            'breadcrumb': breadcrumb
        })

    @http.route('/documents/upload/<int:folder_id>', type='http', auth='public', website=True, csrf=True)
    def upload_file(self, folder_id, **kwargs):
        folder_id = folder_id

        return request.render("docs.file_upload_page", {
            'folder_id': folder_id
        })

    @http.route(['/create_document'], type='http', auth='public', website=True, csrf=True, methods=['POST'])
    def create_document(self, **post):
        # Get the uploaded file
        uploaded_file = request.httprequest.files.get('file')
        folder_id = int(post.get('folder_id'))

        # Check if a file was uploaded
        if not uploaded_file:
            return request.redirect('/documents/folder/%s' % folder_id if folder_id else '/documents')

        # Extract the file name and file data
        file_name = secure_filename(uploaded_file.filename)  # Securely get the original file name
        file_data = uploaded_file.read()  # Read the binary content of the file

        # Create the document record in the database
        request.env['docs.main'].sudo().create({
            'file_name': file_name,
            'file': file_data,
            'folder_id': folder_id,
        })
        
        # Redirect back to the folder view
        return request.redirect('/documents/folder/%s' % folder_id if folder_id else '/documents')
       
    # @http.route(['/documents/createfolder/<int:folder_id>'], type='http', auth='public', website=True, csrf=True)
    # def create_folder(self, folder_id, **kwargs):
    #     # folder_id = folder_id

    #     return request.render("docs.create_folder_page", {
    #         'folder_id': folder_id,
    #     })
    
    @http.route(['/documents/createfolder/<int:folder_id>'], type='http', auth='public', website=True, csrf=True)
    def create_folder_page(self, folder_id, **kwargs):
        folder = request.env['docs.folder'].browse(folder_id)
        if not folder.exists():
            return request.not_found()
        
        return request.render("docs.create_folder_page", {
            'folder_id': folder_id
        })

    @http.route(['/createnewfolder'], type='http', auth='public', website=True, csrf=True)
    def create_folder(self, **post):
        folder_id = int(post.get('folder_id'))
        request.env['docs.folder'].sudo().create({
            'name': post.get('folder_name'),
            'parent_id': folder_id if folder_id else False,
        })
        return request.redirect('/documents/folder/%s' % folder_id if folder_id else '/documents')

    