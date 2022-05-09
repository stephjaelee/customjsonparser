from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings

import os
from .json_parser import CommentedJsonParser


def index(request):
    return HttpResponse("Hello, world. Testing index.")

def upload(request):
    context = {}
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        uploaded_file_obj = open(os.path.join(settings.MEDIA_ROOT, name), 'r')
        uploaded_file_content = uploaded_file_obj.read()
        parsed_json = CommentedJsonParser(uploaded_file_content).parse()
        parsed_json_name = 'parsed_'+name
        parsed_json_path = os.path.join(settings.MEDIA_ROOT, parsed_json_name)
        with open(parsed_json_path, 'w') as f:
            parsed_json_file = File(f)
            parsed_json_file.write(parsed_json)
        context['uploaded_file'] = fs.url(name)
        context['parsed_file'] = fs.url(parsed_json_name)
    return render(request, 'upload.html', context)