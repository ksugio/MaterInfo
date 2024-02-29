from config.settings import REPOS_ROOT
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
from ..models import Repository
import subprocess
import gzip
import base64

def base_auth(header):
    authmeth, auth = header.split(' ', 1)
    if authmeth.lower() == 'basic':
        auth = base64.b64decode(auth.strip()).decode('utf8')
        username, password = auth.split(':', 1)
        user = authenticate(username=username, password=password)
        return user
    else:
        return None

def check_auth(request, func, *args, **kwargs):
    if request.META.get('HTTP_AUTHORIZATION'):
        user = base_auth(request.META['HTTP_AUTHORIZATION'])
        if user:
            pid = kwargs['pid']
            title = kwargs['name'].rstrip('.git')
            repo = Repository.objects.filter(title=title, upper=pid)
            if len(repo) == 1 and user in repo[0].upper.member.all():
                return func(request, *args, **kwargs)
        return HttpResponseForbidden('Forbidden')
    else:
        response = HttpResponse()
        response.status_code = 401
        response['WWW-Authenticate'] = 'Basic'
        return response

def git_login_required(func):
    @wraps(func)
    def _decorator(request, *args, **kwargs):
        return check_auth(request, func, *args, **kwargs)
    return _decorator

@git_login_required
def info_refs(request, pid, name):
    service = request.GET['service']
    path = '%s/%d/%s' % (REPOS_ROOT, pid, name)
    ss = service.split('-')
    cmd = [ss[0], '-'.join(ss[1:]), '--stateless-rpc', '--advertise-refs', path]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    response = HttpResponse()
    response.headers['Expires'] = 'Fri, 01 Jan 1980 00:00:00 GMT'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cache-Control'] = 'no-cache, max-age=0, must-revalidate'
    response.headers['Content-Type'] = 'application/x-%s-advertisement' % service
    packet = '# service=%s\n' % service
    length = len(packet) + 4
    prefix = "{:04x}".format(length & 0xFFFF)
    response.write('{0}{1}0000'.format(prefix, packet))
    response.write(p.stdout.read())
    p.stdout.flush()
    p.wait()
    return response

@csrf_exempt
def git_upload_pack(request, pid, name):
    path = '%s/%d/%s' % (REPOS_ROOT, pid, name)
    if 'Content-Encoding' in request.headers:
        rdata = gzip.decompress(request.body)
    else:
        rdata = request.body
    p = subprocess.Popen(['git', 'upload-pack', '--stateless-rpc', path], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.stdin.write(rdata)
    p.stdin.flush()
    response = HttpResponse()
    response.headers['Expires'] = 'Fri, 01 Jan 1980 00:00:00 GMT'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cache-Control'] = 'no-cache, max-age=0, must-revalidate'
    response.headers['Content-Type'] = 'application/x-git-upload-pack-result'
    response.write(p.stdout.read())
    p.stdout.flush()
    p.wait()
    return response

@csrf_exempt
def git_receive_pack(request, pid, name):
    path = '%s/%d/%s' % (REPOS_ROOT, pid, name)
    p = subprocess.Popen(['git', 'receive-pack', '--stateless-rpc', path], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.stdin.write(request.body)
    p.stdin.flush()
    response = HttpResponse()
    response.headers['Expires'] = 'Fri, 01 Jan 1980 00:00:00 GMT'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cache-Control'] = 'no-cache, max-age=0, must-revalidate'
    response.headers['Content-Type'] = 'application/x-git-receive-pack-result'
    response.write(p.stdout.read())
    p.stdout.flush()
    p.wait()
    return response

