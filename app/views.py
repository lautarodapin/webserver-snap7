from app.models import DatoProcesado
from django.db.models import query
from django.shortcuts import render
from django.http import StreamingHttpResponse
from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin
import time
from django.contrib.auth.models import User
import json

from .serializers import Dato, DatoProcesadoSerializer, DatoSerializer

'''
class ReportCSVViewset(ListModelMixin, viewsets.GenericViewSet):
    queryset = Dato.objects.select_related('stuff')
    serializer_class = DatoSerializer
    renderer_classes = [ReportsRenderer]
    PAGE_SIZE = 1000

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = StreamingHttpResponse(
            request.accepted_renderer.render(self._stream_serialized_data(queryset)),
            status=200,
            content_type="text/csv",
        )
        response["Content-Disposition"] = 'attachment; filename="reports.csv"'
        return response

    def _stream_serialized_data(self, queryset):
        serializer = self.get_serializer_class()
        paginator = Paginator(queryset, self.PAGE_SIZE)
        for page in paginator.page_range:
            yield from serializer(paginator.page(page).object_list, many=True).data
'''
class DatoViewset(viewsets.ModelViewSet):
    queryset = Dato.objects.select_related("area",).prefetch_related("area", "area__filas")
    serializer_class = DatoSerializer

# Create your views here.
def streamed(request):
    sleep_interval = int(request.GET.get('sleep', 10))
    response = StreamingHttpResponse(iterate_users(sleep_interval), content_type='json')
    return response

def iterate_users(sleep_interval):
    queryset = User.objects.all()
    for user in queryset.iterator(chunk_size=1):
        yield json.dumps({"msg":f"{user.username}"})
        time.sleep(sleep_interval)


        
class DatoProcesadoViewset(viewsets.ModelViewSet):
    queryset = DatoProcesado.objects.all()
    serializer_class = DatoProcesadoSerializer
    # lookup_field = "fila_id"

    def get_queryset(self):
        queryset = super().get_queryset()
        filtered = self.request.GET.get("fila_id")
        if filtered:
            queryset = queryset.filter(fila_id=filtered)
        return queryset