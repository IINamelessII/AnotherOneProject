import json
import os
import shutil
import time
from secrets import token_urlsafe

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework import viewsets

from main.decorators import load_data, post_only
from main.forms import UploadFileForm
from main.models import Dir, File, Stats
from main.permissions import IsReadOnly
from main.serializers import DirSerializer, FileSerializer


class DirViewSet(viewsets.ModelViewSet):
    """"API List of all dirs in system"""
    queryset = Dir.objects.all()
    serializer_class = DirSerializer
    permission_classes = (IsReadOnly,)


class FileViewSet(viewsets.ModelViewSet):
    """"API List of all files in system"""
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = (IsReadOnly,)


def add_message_to_session(request, message):
    """Add a message to the session, used by server side"""
    i = 0

    if 'messages' in request.session:
        while str(i) in request.session['messages']:
            i += 1
    else:
        request.session['messages'] = dict()

    request.session.modified = True
    request.session['messages'][i] = message
    return request


def messages(request):
    """"Return all messages in the session"""
    return HttpResponse(json.dumps(request.session.get('messages', dict())), status=200)


def stats(request):
    """Return all stats"""
    data = {
        'downloads': Stats.objects.get(pk=settings.STATS_ID).file_downloads,
        'uploads': Stats.objects.get(pk=settings.STATS_ID).file_uploads,
    }
    return HttpResponse(json.dumps(data), status=200)


def user_data(request):
    """Return cureent user photo and id if user is authenticated via OAuth"""
    if hasattr(request.user, 'socialaccount_set') and len(request.user.socialaccount_set.all()):
        data = {
            'photo': request.user.socialaccount_set.all()[0].extra_data['picture'],
            'id': request.user.id,
        }
    else:
        data = None
    return HttpResponse(json.dumps(data), status=200)


@post_only
@load_data('key')
def unset_message(request, data):
    """Remove message from session"""
    request.session.modified = True
    del request.session['messages'][str(data['key'])]
    return HttpResponse(status=200)


def index(request):
    """Render SPA"""
    return render(request, 'index.html')


@post_only
@load_data('id')
def download(request, data):
    """Return link for downloading file by its id"""
    the_file = File.objects.get(pk=data['id'])
    response = HttpResponse(settings.MEDIA_URL + the_file.file.name)
    response['Content-Disposition'] = f'attachment; filename={the_file.full_name}'

    the_file.inc_download()
    return response

       
@post_only
@load_data('id')
def archive(request, data):
    """Create archive from dir and return link for downloading by dir's id"""
    token = Dir.objects.get(pk=data['id']).archieve_token()
    response = HttpResponse(settings.ARCHIVES_URL + token + '.zip')
    response['Content-Disposition'] = 'attachment; filename={}'.format(token)

    return response
        

@post_only
@load_data('token')
def archive_received(request, data):
    """Remove archive with given token after specified time"""
    time.sleep(settings.TIME_TO_DELETE)
    try:
        Dir.clear_archieve_data(data['token'])
    except:
        return HttpResponse(status=404)
    return HttpResponse(status=200)


@post_only
@login_required
def upload_files(request, id):
    """Upload file to dir with given id"""
    try:
        for the_file in request.FILES.getlist('file'):
            File.upload(the_file, id, request.user, lambda msg: add_message_to_session(request, msg))
    except:
        return HttpResponse(status=401)
    return HttpResponse(status=200)


@post_only
@login_required
@load_data('dirId', 'value')
def add_new_dir(request, data):
    """Add New Directory with given name to the directory with the given dirId"""
    Dir.add_new(data['value'], data['dirId'], request.user, lambda msg: add_message_to_session(request, msg))
    return HttpResponse(status=200)


@post_only
@login_required
def upload_dir(request, id):
    """Upload dir to dir with given id"""
    try:
        Dir.upload(request.FILES.getlist('file'), json.load(request.FILES['relPaths'].file), id, request.user, lambda msg: add_message_to_session(request, msg))
    except:
        return HttpResponse(status=401)
    return HttpResponse(status=200)


@post_only
@login_required
@load_data('id')
def remove_dir(request, data):
    """Remove directory if it requested by its owner"""
    Dir.objects.get(pk=data['id']).safe_delete(request.user, lambda msg: add_message_to_session(request, msg))
    return HttpResponse(status=200)


@post_only
@login_required
@load_data('id', 'dirId', 'name')
def rename_dir(request, data):
    """Rename directory if it requested by its owner"""
    Dir.objects.get(pk=data['id']).safe_rename(request.user, data['name'], data['dirId'], lambda msg: add_message_to_session(request, msg))
    return HttpResponse(status=200)


@post_only
@login_required
@load_data('id')
def remove_file(request, data):
    """Remove file if it requested by its owner"""
    File.objects.get(pk=data['id']).safe_delete(request.user, lambda msg: add_message_to_session(request, msg))
    return HttpResponse(status=200)


@post_only
@login_required
@load_data('id', 'dirId', 'name')
def rename_file(request, data):
    """Rename file if it requested by its owner"""
    File.objects.get(pk=data['id']).safe_rename(request.user, data['name'], data['dirId'], lambda msg: add_message_to_session(request, msg))
    return HttpResponse(status=200)
