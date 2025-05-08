from django.utils.module_loading import import_string
from celery import shared_task, current_task
from accounts.models import CustomUser
from datetime import datetime
import json

@shared_task(name='clone-task', queue='project')
def CloneTask(remote_name, rooturl, id, access, auth, url, cookies,
              scan_lower, set_remote, upper_name, upper_id, **kwargs):
    option = {
        'rooturl': rooturl,
        'auth': auth,
        'cookies': cookies,
        'jwt_access': access,
        'scan_lower': scan_lower
    }
    remote = import_string(remote_name)()
    clone_list = remote.clone_list(id, **option)
    if clone_list is not None:
        option = {
            'rooturl': rooturl,
            'auth': auth,
            'linkurl': url,
            'cookies': cookies,
            'jwt_access': access,
            'root_remoteid': id,
            'root_model': remote.model,
            'scan_lower': scan_lower,
            'set_remote': set_remote
        }
        request_user = CustomUser.objects.get(id=kwargs['request_user_id'])
        if upper_name:
            cls = import_string(upper_name)
            upper = cls.objects.get(pk=upper_id)
            kwargs, objects = remote.clone_exec(clone_list, upper, request_user, **option)
        else:
            kwargs, objects = remote.clone_exec(clone_list, None, request_user, **option)
        model = objects[0]
        if current_task.request.id:
            model.task_id = current_task.request.id
        if hasattr(model, 'remotelog'):
            remotelog = [{
                'task': 'cloned',
                'username': request_user.username,
                'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'lines': remote.get_pull_list_text(clone_list)
            }]
            model.remotelog = json.dumps(remotelog)
            model.save(localupd=False)
    return 'Finished'

@shared_task(name='pull-task', queue='project')
def PullTask(remote_name, id, access, cookies, **kwargs):
    remote = import_string(remote_name)()
    model = remote.model.objects.get(id=id)
    option = {
        'rooturl': model.remoteurl,
        'auth': model.remoteauth,
        'cookies': cookies,
        'jwt_access': access,
        'scan_lower': True
    }
    pull_list = remote.pull_list(model, **option)
    option = {
        'rooturl': model.remoteurl,
        'auth': model.remoteauth,
        'linkurl': model.remotelink,
        'cookies': cookies,
        'jwt_access': access,
        'root_remoteid': model.remoteid,
        'root_model': remote.model,
        'scan_lower': True,
        'set_remote': True
    }
    request_user = CustomUser.objects.get(id=kwargs['request_user_id'])
    remote.pull_exec(pull_list, model, request_user, **option)
    if hasattr(model, 'remotelog'):
        remotelog = json.loads(model.remotelog)
        remotelog.append({
            'task': 'pulled',
            'username': request_user.username,
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'lines': remote.get_pull_list_text(pull_list)
        })
        model.remotelog = json.dumps(remotelog)
        model.save(localupd=False)
    return 'Finished'

@shared_task(name='push-task', queue='project')
def PushTask(remote_name, id, access, cookies, **kwargs):
    remote = import_string(remote_name)()
    model = remote.model.objects.get(id=id)
    option = {
        'rooturl': model.remoteurl,
        'auth': model.remoteauth,
        'cookies': cookies,
        'jwt_access': access,
        'scan_lower': True
    }
    push_list = remote.push_list(model, **option)
    option = {
        'rooturl': model.remoteurl,
        'auth': model.remoteauth,
        'cookies': cookies,
        'jwt_access': access
    }
    request_user = CustomUser.objects.get(id=kwargs['request_user_id'])
    remote.push_exec(push_list, **option)
    if hasattr(model, 'remotelog'):
        remotelog = json.loads(model.remotelog)
        remotelog.append({
            'task': 'pushed',
            'username': request_user.username,
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'lines': remote.get_push_list_text(push_list)
        })
        model.remotelog = json.dumps(remotelog)
        model.save(localupd=False)
    return 'Finished'
