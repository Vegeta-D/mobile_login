# -*- coding: utf-8 -*-

{
    'name': 'Mobile Login',
    'version': '1.0',
    'category': 'Tools',
    'sequence': 20,
    'author': 'Beijing Lishi Technology Co.,Ltd',
    'summary': 'Enable mobile number login',
    'description': """
            Enable users to login using mobile number
            Features:
            - Supports mobile phone number login
            - Mobile phone number format verification
            - Email login compatible
        """,
    'website': '',
    'depends': ['base', 'auth_signup'],
    'data': [
        'views/res_users_views.xml',
        'views/login_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
