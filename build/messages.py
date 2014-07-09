# -*- coding: utf-8 -*-

#: Default Flask-Security configuration
_default_config = {
    'BLUEPRINT_NAME': 'security',
    'URL_PREFIX': None,
    'SUBDOMAIN': None,
    'FLASH_MESSAGES': True,
    'PASSWORD_HASH': 'plaintext',
    'PASSWORD_SALT': None,
    'LOGIN_URL': '/login',
    'LOGOUT_URL': '/logout',
    'REGISTER_URL': '/register',
    'RESET_URL': '/reset',
    'CHANGE_URL': '/change',
    'CONFIRM_URL': '/confirm',
    'POST_LOGIN_VIEW': '/',
    'POST_LOGOUT_VIEW': '/',
    'CONFIRM_ERROR_VIEW': None,
    'POST_REGISTER_VIEW': None,
    'POST_CONFIRM_VIEW': None,
    'POST_RESET_VIEW': None,
    'POST_CHANGE_VIEW': None,
    'UNAUTHORIZED_VIEW': None,
    'FORGOT_PASSWORD_TEMPLATE': 'security/forgot_password.html',
    'LOGIN_USER_TEMPLATE': 'security/login_user.html',
    'REGISTER_USER_TEMPLATE': 'security/register_user.html',
    'RESET_PASSWORD_TEMPLATE': 'security/reset_password.html',
    'CHANGE_PASSWORD_TEMPLATE': 'security/change_password.html',
    'SEND_CONFIRMATION_TEMPLATE': 'security/send_confirmation.html',
    'SEND_LOGIN_TEMPLATE': 'security/send_login.html',
    'CONFIRMABLE': False,
    'REGISTERABLE': False,
    'RECOVERABLE': False,
    'TRACKABLE': False,
    'PASSWORDLESS': False,
    'CHANGEABLE': False,
    'SEND_REGISTER_EMAIL': True,
    'SEND_PASSWORD_CHANGE_EMAIL': True,
    'SEND_PASSWORD_RESET_NOTICE_EMAIL': True,
    'LOGIN_WITHIN': '1 days',
    'CONFIRM_EMAIL_WITHIN': '5 days',
    'RESET_PASSWORD_WITHIN': '5 days',
    'LOGIN_WITHOUT_CONFIRMATION': False,
    'EMAIL_SENDER': 'no-reply@localhost',
    'TOKEN_AUTHENTICATION_KEY': 'auth_token',
    'TOKEN_AUTHENTICATION_HEADER': 'Authentication-Token',
    'CONFIRM_SALT': 'confirm-salt',
    'RESET_SALT': 'reset-salt',
    'LOGIN_SALT': 'login-salt',
    'CHANGE_SALT': 'change-salt',
    'REMEMBER_SALT': 'remember-salt',
    'DEFAULT_REMEMBER_ME': False,
    'DEFAULT_HTTP_AUTH_REALM': 'Login Required',
    'EMAIL_SUBJECT_REGISTER': u'Hoşgeldin!',
    'EMAIL_SUBJECT_CONFIRM': u'Lütfen e-postanı onayla',
    'EMAIL_SUBJECT_PASSWORDLESS': u'Giriş yönlendirmesi',
    'EMAIL_SUBJECT_PASSWORD_NOTICE': u'Şifren sıfırlandı',
    'EMAIL_SUBJECT_PASSWORD_CHANGE_NOTICE': u'Şifren değiştirildi',
    'EMAIL_SUBJECT_PASSWORD_RESET': u'Şifre sıfırlama',
    'USER_IDENTITY_ATTRIBUTES': ['email']
}

# security_messages = dict()
security_messages = {
    'UNAUTHORIZED': ('You do not have permission to view this resource.', 'error'),
    'CONFIRM_REGISTRATION': ('Thank you. Confirmation instructions have been sent to %(email)s.', 'success'),
    'EMAIL_CONFIRMED': (u'Teşekkürler. E-posta adresin doğrulandı.', 'success'),
    'ALREADY_CONFIRMED': (u'E-posta adresin çoktan doğrulandı.', 'info'),
    'INVALID_CONFIRMATION_TOKEN': ('Invalid confirmation token.', 'error'),
    'EMAIL_ALREADY_ASSOCIATED': (u'Bu e-posta başka bir hesap ile ilişkili.', 'error'),
    'PASSWORD_MISMATCH': (u'Şifre eşleşmiyor', 'error'),
    'RETYPE_PASSWORD_MISMATCH': (u'Şifreler eşleşmiyor', 'error'),
    'INVALID_REDIRECT': ('Redirections outside the domain are forbidden', 'error'),
    'PASSWORD_RESET_REQUEST': (u'Şifreni sıfırlamak için gerekli bilgi e-posta adresine gönderildi.', 'info'),
    'PASSWORD_RESET_EXPIRED': ('You did not reset your password within %(within)s. New instructions have been sent to %(email)s.', 'error'),
    'INVALID_RESET_PASSWORD_TOKEN': ('Invalid reset password token.', 'error'),
    'CONFIRMATION_REQUIRED': ('Email requires confirmation.', 'error'),
    'CONFIRMATION_REQUEST': ('Confirmation instructions have been sent to %(email)s.', 'info'),
    'CONFIRMATION_EXPIRED': ('You did not confirm your email within %(within)s. New instructions to confirm your email have been sent to %(email)s.', 'error'),
    'LOGIN_EXPIRED': ('You did not login within %(within)s. New instructions to login have been sent to %(email)s.', 'error'),
    'LOGIN_EMAIL_SENT': ('Instructions to login have been sent to %(email)s.', 'success'),
    'INVALID_LOGIN_TOKEN': ('Invalid login token.', 'error'),
    'DISABLED_ACCOUNT': (u'Hesap aktif değil', 'error'),
    'EMAIL_NOT_PROVIDED': (u'E-postanı girmelisin', 'error'),
    'INVALID_EMAIL_ADDRESS': (u'Geçersiz e-posta adresi', 'error'),
    'PASSWORD_NOT_PROVIDED': (u'Şifreni girmelisin', 'error'),
    'PASSWORD_NOT_SET': (u'Şifre oluşturulmamış', 'error'),
    'PASSWORD_INVALID_LENGTH': (u'Şifren en az 6 karakter olmalı.', 'error'),
    'USER_DOES_NOT_EXIST': (u'Böyle bir kullanıcı bulamadık', 'error'),
    'INVALID_PASSWORD': (u'Hatalı şifre', 'error'),
    'PASSWORDLESS_LOGIN_SUCCESSFUL': (u'Başarıyla giriş yaptın.', 'success'),
    'PASSWORD_RESET': (u'Şifren başarıyla sıfırlandı.', 'success'),
    'PASSWORD_IS_THE_SAME': (u'Yeni şifren, bir önceki şifrende farklı olmalı', 'error'),
    'PASSWORD_CHANGE': (u'Şifreni başarıyla değiştirdin.', 'success'),
    'LOGIN': (u'Bu sayfaya ulaşmak için lütfen giriş yapın.', 'info'),
    'REFRESH': (u'Bu sayfaya ulaşmak için lütfen yeniden giriş yapın.', 'info'),
    # reautanticate
}
