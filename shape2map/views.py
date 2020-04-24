import os
import json
import shutil
import shapefile
from django.conf import settings
from django.shortcuts import render
from django.views.generic import View
from geojson_rewind import rewind
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage


def shapeConv(file_url):
    reader = shapefile.Reader(file_url)
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    buffer = []
    for sr in reader.shapeRecords():
        atr = dict(zip(field_names, sr.record))
        geom = sr.shape.__geo_interface__
        buffer.append(dict(type="Feature",
                           geometry=geom, properties=atr))
    data = json.dumps({"type": "FeatureCollection",
                       "features": buffer}, indent=2)
    return rewind(data)


class Index(View):

    def get(self, request, *args, **kwargs):
        template = 'index.html'
        return render(request, template)

    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist('files')
        if files:
            shutil.rmtree(os.path.join(settings.MEDIA_ROOT))
        fs = FileSystemStorage()
        shp_file = ''
        for f in files:
            file = fs.save(f.name, f)
            file_url = os.path.join(settings.MEDIA_ROOT, file)
            if file_url.endswith(".shp"):
                shp_file = file_url
        data = shapeConv(shp_file)
        if data:
            shutil.rmtree(os.path.join(settings.MEDIA_ROOT))
        else:
            pass
        return HttpResponse(data)
