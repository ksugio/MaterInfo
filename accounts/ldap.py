from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from ldap3 import Server, Connection, MODIFY_REPLACE
from config import settings
from project.models import CreateUserProject
from .models import CustomUser

def SearchUser(username):
    try:
        server = Server(settings.LDAP_SERVER['HOST'],
                        port=settings.LDAP_SERVER['PORT'],
                        use_ssl=settings.LDAP_SERVER['USE_SSL'])
        conn = Connection(server, auto_bind=True)
        search_filter = '(%s=%s)' % (settings.LDAP_SERVER['USERNAME'], username)
        attributes = [ 'cn',
            settings.LDAP_SERVER['USERNAME'],
            settings.LDAP_SERVER['EMAIL'],
            settings.LDAP_SERVER['FIRST_NAME'],
            settings.LDAP_SERVER['LAST_NAME']
        ]
        conn.search(settings.LDAP_SERVER['SEARCH_BASE'],
                    search_filter, attributes=attributes)
        if len(conn.entries) > 0:
            entry = conn.entries[0]
        else:
            entry = None
        conn.unbind()
        return entry
    except:
        return None

def LoginCheck(entry, password):
    try:
        server = Server(settings.LDAP_SERVER['HOST'],
                        port=settings.LDAP_SERVER['PORT'],
                        use_ssl=settings.LDAP_SERVER['USE_SSL'])
        conn = Connection(server, user=entry.entry_dn, password=password)
        res = conn.bind()
        conn.unbind()
        return res
    except:
        return False

def CreateUser(entry, username, password):
    kwargs = {'username': username, 'password': make_password(password)}
    first_name = entry[settings.LDAP_SERVER['FIRST_NAME']]
    if  len(first_name) > 0:
        kwargs['first_name'] = first_name
    last_name = entry[settings.LDAP_SERVER['LAST_NAME']]
    if len(last_name) > 0:
        kwargs['last_name'] = last_name
    email = entry[settings.LDAP_SERVER['EMAIL']]
    if len(email) > 0:
        kwargs['email'] = email
    user = CustomUser.objects.create(**kwargs)
    if settings.LDAP_SERVER['CREATE_USER_PROJECT']:
        CreateUserProject(user)
    return user

def UpdateUser(entry, user, password):
    user.password = make_password(password)
    first_name = entry[settings.LDAP_SERVER['FIRST_NAME']]
    if  len(first_name) > 0:
        user.first_name = first_name
    last_name = entry[settings.LDAP_SERVER['LAST_NAME']]
    if len(last_name) > 0:
        user.last_name = last_name
    email = entry[settings.LDAP_SERVER['EMAIL']]
    if len(email) > 0:
        user.email = email
    user.save()
    return user

class LDAPBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None):
        entry = SearchUser(username)
        if entry is None:
            return None
        if LoginCheck(entry, password):
            users = CustomUser.objects.filter(username=username)
            if len(users) > 0:
                return UpdateUser(entry, users[0], password)
            else:
                return CreateUser(entry, username, password)
        return None

def LDAPUpdateUser(username, first_name, last_name, email):
    server = Server(settings.LDAP_SERVER['HOST'],
                    port=settings.LDAP_SERVER['PORT'],
                    use_ssl=settings.LDAP_SERVER['USE_SSL'])
    conn = Connection(server, user=settings.LDAP_SERVER['USER'],
                      password=settings.LDAP_SERVER['PASSWORD'],
                      auto_bind=True)
    search_filter = '(%s=%s)' % (settings.LDAP_SERVER['USERNAME'], username)
    conn.search(settings.LDAP_SERVER['SEARCH_BASE'], search_filter)
    if len(conn.entries) > 0:
        entry = conn.entries[0]
        changes = {settings.LDAP_SERVER['FIRST_NAME']: [(MODIFY_REPLACE, [first_name])],
                   settings.LDAP_SERVER['LAST_NAME']: [(MODIFY_REPLACE, [last_name])],
                   settings.LDAP_SERVER['EMAIL']: [(MODIFY_REPLACE, [email])]}
        conn.modify(entry.entry_dn, changes)
    conn.unbind()
    return conn.result

def LDAPChangePassword(username, old_password, new_password):
    server = Server(settings.LDAP_SERVER['HOST'],
                    port=settings.LDAP_SERVER['PORT'],
                    use_ssl=settings.LDAP_SERVER['USE_SSL'])
    conn = Connection(server, user=settings.LDAP_SERVER['USER'],
                      password=settings.LDAP_SERVER['PASSWORD'],
                      auto_bind=True)
    search_filter = '(%s=%s)' % (settings.LDAP_SERVER['USERNAME'], username)
    conn.search(settings.LDAP_SERVER['SEARCH_BASE'], search_filter)
    if len(conn.entries) > 0:
        entry = conn.entries[0]
        conn.extend.standard.modify_password(entry.entry_dn, old_password, new_password)
    conn.unbind()
    return conn.result
