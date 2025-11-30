# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessDenied, ValidationError
import re
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    mobile_login = fields.Char(
        string='Mobile Login',
        index=True,
        help='Use for mobile number login'
    )

    _sql_constraints = [
        ('mobile_login_unique', 'unique(mobile_login)', 'Mobile number must be unique!'),
    ]

    @api.constrains('mobile_login')
    def _check_mobile_format(self):
        for user in self:
            if user.mobile_login and not self._is_valid_mobile(user.mobile_login):
                raise ValidationError(_('Invalid mobile number format, please enter 11-digit valid mobile number'))

    def _is_valid_mobile(self, mobile):
        if not mobile:
            return False
        mobile_pattern = r'^1[3-9]\d{9}$'
        return re.match(mobile_pattern, mobile) is not None

    @classmethod
    def authenticate(cls, db, login, password):
        if isinstance(login, dict):
            login_str = login.get('login', '')
            _logger.info("Authentication attempt - Login dict received")
        else:
            login_str = str(login) if login else ""

        _logger.info("Processing login: %s", login_str)

        if not login_str or not password:
            raise AccessDenied(_("Login or password is missing"))
        try:
            uid = super().authenticate(db, login, password)
            if uid:
                _logger.info("Email authentication successful: %s", login_str)
                return uid
        except AccessDenied:
            _logger.info("Email authentication failed, trying mobile authentication: %s", login_str)
            pass
        mobile_pattern = r'^1[3-9]\d{9}$'
        if login_str and re.match(mobile_pattern, login_str):
            _logger.info("Detected mobile number format, trying mobile authentication: %s", login_str)

            try:
                from odoo.sql_db import db_connect

                with db_connect(db).cursor() as cr:
                    cr.execute("""
                        SELECT login, id FROM res_users 
                        WHERE mobile_login = %s AND active = true 
                        LIMIT 1
                    """, (login_str,))

                    result = cr.fetchone()
                    if result:
                        user_login = result[0]
                        user_id = result[1]
                        _logger.info("Found mobile user - Login: %s, ID: %s", user_login, user_id)

                        if isinstance(login, dict):
                            mobile_credential = login.copy()
                            mobile_credential['login'] = user_login
                        else:
                            mobile_credential = user_login

                        try:
                            uid = super().authenticate(db, mobile_credential, password)
                            if uid:
                                _logger.info("Mobile authentication successful for user ID: %s", uid)
                                return uid
                            else:
                                _logger.warning("Mobile user found but authentication failed: %s", login_str)
                        except AccessDenied:
                            _logger.warning("Mobile authentication - Password incorrect for user: %s", user_login)
                            raise

                    else:
                        _logger.info("No mobile user found for: %s", login_str)

            except AccessDenied:
                raise
            except Exception as e:
                _logger.error("Mobile authentication error: %s", str(e))

        _logger.warning("All authentication methods failed for login: %s", login_str)
        raise AccessDenied(_("Wrong login or password"))