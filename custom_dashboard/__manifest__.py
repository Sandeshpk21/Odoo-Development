# -*- coding: utf-8 -*-
{
    'name': "custom_dashboard",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'sequence': -1,
    'description': """
Long description of module's purpose
    """,

    'author': "Sandesh S Patilkulkarni Vivanet",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','asset_management','web','board'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/dashboard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_dashboard/static/src/components/**/*.js',
            'custom_dashboard/static/src/components/**/*.xml',
            'custom_dashboard/static/src/components/**/*.scss',
        ]
    },

    'installable': True,
    'application': True,
}

