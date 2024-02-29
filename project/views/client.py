from django.shortcuts import render, redirect
from django.urls import reverse
from . import base
import socket
import ssl
import json
import base64
import time

HeadBytes = 4
BufSize = 65536

def Connect(server):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        if server['ssl_use']:
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            context.verify_mode = ssl.CERT_NONE
            context.check_hostname = False
            sock = context.wrap_socket(sock, server_hostname=server['ipaddr'])
        sock.connect((server['ipaddr'], server['port']))
        return sock
    except:
        return None

def Send(sock, ddata):
    data = json.dumps(ddata).encode()
    lb = len(data).to_bytes(HeadBytes, byteorder="little")
    if sock.send(lb) == HeadBytes:
        sock.sendall(data)

def Recv(sock):
    try:
        lb = sock.recv(HeadBytes)
    except TimeoutError:
        return {}
    size = int.from_bytes(lb, byteorder="little")
    data = b''
    while len(data) < size:
        data += sock.recv(BufSize)
    ddata = json.loads(data.decode())
    return ddata

def Alive(server):
    sock = Connect(server)
    if sock:
        sock.close()
        return True
    else:
        return False

def Submit(server, user, **kwargs):
    sock = Connect(server)
    if sock:
        kwargs['token'] = server['token']
        kwargs['user'] = str(user) + '@' + socket.gethostname()
        kwargs['method'] = 'SUBMIT'
        Send(sock, kwargs)
        rddata = Recv(sock)
        sock.close()
        return rddata
    else:
        return None

def Cancel(server, id):
    sock = Connect(server)
    if sock:
        ddata = {
            'token': server['token'],
            'method': 'CANCEL',
            'id': id,
        }
        Send(sock, ddata)
        rddata = Recv(sock)
        sock.close()
        return rddata
    else:
        return None

def Jobs(server, status):
    sock = Connect(server)
    if sock:
        ddata = {
            'token': server['token'],
            'method': 'JOBS',
            'status': status,
        }
        Send(sock, ddata)
        rddata = Recv(sock)
        return rddata
    else:
        return None

def Job(server, id):
    sock = Connect(server)
    if sock:
        ddata = {
            'token': server['token'],
            'method': 'JOB',
            'id': id,
        }
        Send(sock, ddata)
        rddata = Recv(sock)
        sock.close()
        return rddata
    else:
        return None

def Get(server, id, ext):
    sock = Connect(server)
    if sock:
        ddata = {
            'token': server['token'],
            'method': 'GET',
            'id': id,
            'ext': ext,
        }
        Send(sock, ddata)
        rddata = Recv(sock)
        sock.close()
        return rddata
    else:
        return None

def Clear(server, id):
    sock = Connect(server)
    if sock:
        ddata = {
            'token': server['token'],
            'method': 'CLEAR',
            'id': id,
        }
        Send(sock, ddata)
        rddata = Recv(sock)
        sock.close()
        return rddata
    else:
        return None

def Extra(server, method, **kwargs):
    sock = Connect(server)
    if sock:
        kwargs['token'] = server['token']
        kwargs['method'] = method
        Send(sock, kwargs)
        rddata = Recv(sock)
        sock.close()
        return rddata
    else:
        return None

def Base64Encode(data):
    return base64.b64encode(data).decode('utf-8')

def Base64Decode(b64data):
    return base64.b64decode(b64data.encode())

class AddView(base.AddView):
    model = None
    upper = None
    form_class = None
    template_name ="project/default_add.html"
    server_list = None

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        choices = []
        for i in range(len(self.server_list)):
            if Alive(self.server_list[i]):
                choices.append((i, self.server_list[i]['name']))
        form.fields['server'].choices = choices
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.cleaned_data['submit']:
            model = form.save(commit=False)
            ddata = self.get_ddata(model)
            rddata = Submit(self.server_list[model.server], self.request.user, **ddata)
            if rddata:
                model.job_id = rddata['id']
                model.job_uuid = rddata['uuid']
                model.job_status = rddata['status']
                model.save()
        return response

    def get_ddata(self, model):
        pass

class DetailView(base.DetailView):
    model = None
    template_name = ""
    server_list = None

    def server_info(self, server_id):
        if server_id < len(self.server_list):
            return self.server_list[server_id]
        else:
            return {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        server_info = self.server_info(model.server)
        if 'name' in server_info:
            context['servername'] = server_info['name']
            if model.job_status == 'waiting' or model.job_status == 'running' or model.job_status == 'stop':
                rddata = Job(server_info, model.job_id)
                if rddata:
                    if rddata['status'] != model.job_status or rddata['order'] != model.job_order:
                        if rddata['status'] == 'finished' or rddata['status'] == 'terminated':
                            self.set_model(server_info, model)
                        model.job_status = rddata['status']
                        model.job_order = rddata['order']
                        model.save()
                        context['object'] = model
        return context

    def set_model(self, server, model):
        pass

class UpdateView(base.UpdateView):
    model = None
    form_class = None
    template_name = "project/default_update.html"
    server_list = None

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        choices = []
        for i in range(len(self.server_list)):
            if Alive(self.server_list[i]):
                choices.append((i, self.server_list[i]['name']))
        form.fields['server'].choices = choices
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.cleaned_data['submit']:
            model = form.save(commit=False)
            ddata = self.get_ddata(model)
            Clear(self.server_list[model.server], model.job_id)
            rddata = Submit(self.server_list[model.server], self.request.user, **ddata)
            if rddata:
                model.job_id = rddata['id']
                model.job_uuid = rddata['uuid']
                model.job_status = rddata['status']
                model.save()
        return response

    def get_ddata(self, model):
        pass

class DeleteView(base.DeleteView):
    model = None
    template_name = "project/default_delete.html"
    error_template_name = 'project/default_delete_error.html'
    bdcl_remove = 0
    server_list = None

    def post(self, request, *args, **kwargs):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        if model.server < len(self.server_list):
            Clear(self.server_list[model.server], model.job_id)
        return super().post(request, *args, **kwargs)

class DeleteManagerView(base.DeleteManagerView):
    model = None
    template_name = "project/default_delete.html"
    server_list = None

    def post(self, request, *args, **kwargs):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        if model.server < len(self.server_list):
            Clear(self.server_list[model.server], model.job_id)
        return super().post(request, *args, **kwargs)

class CancelView(base.View):
    model = None
    template_name = "project/default_cancel.html"
    success_name = ''
    server_list = None
    sleep = 0

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        params = {
            'object': model,
            'brand_name': self.brandName(),
            'breadcrumb_list': self.breadcrumbList(model)
        }
        return render(request, self.template_name, params)

    def post(self, request, **kwargs):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        Cancel(self.server_list[model.server], model.job_id)
        if self.sleep > 0:
            time.sleep(self.sleep)
        return redirect(reverse(self.success_name, kwargs={'pk': model.id}))

class JobsView(base.View):
    model = None
    upper = None
    template_name = "project/default_jobs.html"
    list_name = ''
    server_list = None

    def get(self, request, **kwargs):
        upper = self.upper.objects.get(pk=kwargs['pk'])
        jobs_list = []
        down_list = []
        for server in self.server_list:
            jobs = Jobs(server, 'running:waiting')
            if jobs is not None:
                for job in jobs:
                    job['server'] = server['name']
                    jobs_list.append(job)
            else:
                down_list.append(server['name'])
        params = {
            'title': self.model.__name__ + ' Jobs',
            'jobs_list': jobs_list,
            'down_list': down_list,
            'list_url': reverse(self.list_name, kwargs={'pk': upper.id}),
            'brand_name': self.brandName(),
            'breadcrumb_list': self.breadcrumbDetail(upper),
        }
        return render(request, self.template_name, params)
