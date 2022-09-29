from pysendpulse.pysendpulse import PySendPulse

def mailing():
    REST_API_ID = 'e071900fe5ab9aa6dd4dec2f42160ead'
    REST_API_SECRET = '7e82daa1ccfd678487a894b3e3487967'
    TOKEN_STORAGE = 'memcached'
    MEMCACHED_HOST = '127.0.0.1:11211'
    SPApiProxy = PySendPulse(REST_API_ID, REST_API_SECRET, TOKEN_STORAGE, memcached_host=MEMCACHED_HOST)
    return SPApiProxy

def send_mail(subject, html, text, to_name, to_email):
    email = {
        'subject': subject,
        'html': html,
        'text': text,
        'from': {'name': 'ЦОПП СО', 'email': 'bvb@copp63.ru'},
        'to': [
            {'name': to_name, 'email': to_email}
        ],
    }
    SPApiProxy = mailing()
    SPApiProxy.smtp_send_mail(email)
    return "Ok"