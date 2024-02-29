from django.urls import reverse
from config.settings import USE_LOCAL_HOST
import requests

def Login(rooturl, username, password):
    url = rooturl + '/api/auth/jwt/create/'
    data = {'username': username, 'password': password}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        refresh = response.json()['refresh']
        access = response.json()['access']
        return refresh, access
    else:
        return None, None

def GetAccessToken(rooturl, refresh):
    url = rooturl + '/api/auth/jwt/refresh/'
    data = {'refresh': refresh }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()['access']
    else:
        return None

def GetSessionAccessToken(rooturl, session):
    if rooturl in session:
        refresh = session[rooturl]
        access = GetAccessToken(rooturl, refresh)
        if access is not None:
            return access
        else:
            del session[rooturl]
            return 'InvalidToken'
    else:
        return 'NoToken'

def SetSessionRefreshToken(rooturl, session, refresh):
    session[rooturl] = refresh

def VerifyAccessToken(rooturl, refresh, access):
    url = rooturl + '/api/auth/jwt/verify/'
    data = {'token': access }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return access
    else:
        return GetAccessToken(rooturl, refresh)

def VerifyID(rooturl, retrieve_name, access, id):
    url = '%s%s' % (rooturl, reverse(retrieve_name, kwargs={'pk': id}))
    headers = {'Authorization': 'JWT %s' % (access)}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def CheckURL(url):
    if USE_LOCAL_HOST['check']:
        hosts = USE_LOCAL_HOST['hosts']
        localhost = USE_LOCAL_HOST['localhost']
        for host in hosts:
            if url.find(host) >= 0:
                url = url.replace(host, localhost)
    return url

def ParseURL(url, view_name, view_args):
    id = url.split('/')[-view_args]
    path = reverse(view_name, args=range(view_args))
    path = path[:-(2*view_args-1)]
    pp = url.find(path)
    if pp > 0 and id.isdigit():
        rooturl = CheckURL(url[:pp])
        id = int(id)
        return rooturl, id
    else:
        return url, 0
