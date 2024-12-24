# -*- coding: utf-8 -*-
{
    'name': "Docs",
    'summary': "Module for managing documents with metadata and version control.",

    'description': """
    This module allows users to upload documents, manage metadata,
        track versions, and view the author, creation date, and modification date.
    """,

    'author': "Sandesh S Patilkulkarni Vivanet",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','website'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/main_views.xml',
        'views/folder_view.xml',
        'views/file_view.xml',
        'views/folder_kanban.xml',
        'views/menu.xml',
        'views/website_docs.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}

