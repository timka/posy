import tg
import copy
import smtplib
import socket
import logging
import datetime


def path_join(*args):
    return '/'.join(args)


class password_dict(dict):
    def __repr__(self):
        return repr(clear_passwords(dict(self), asterisks=True))

    def __str__(self):
        return str(clear_passwords(dict(self), asterisks=True))


def clear_passwords(data, asterisks=False):
    '''
    Return a deep copy of `data` dict with all passwords deleted or
    replaced with asterisks, if `asterisks` is set to True.
    '''
    def recurse(data):
        if 'password' in data:
            if asterisks:
                data['password'] = '*' * 8
            else:
                del data['password']
        for key, value in data.items():
            if hasattr(value, 'items'):
                recurse(value)
        return data

    data = copy.deepcopy(data)
    return recurse(data)
    

def send_email(lines, to_address, from_address, subject):
    headers = [
        "To: %s" % to_address,
        "From: %s" % from_address,
        "Subject: %s" % subject,
    ]
    body = '''Server time: %s
''' % datetime.datetime.utcnow().strftime('%F %T UTC')
    messages = '\n'.join(lines)
    body += messages
    message = '\n'.join(headers) + "\n\n" + body
    logging.debug('send_email: locals(): %s', locals())
    host = tg.config.smtp_server or 'localhost'
    server = smtplib.SMTP(host)
    server.sendmail(from_address, [to_address], message)
    server.quit()
