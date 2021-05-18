from django_filters import rest_framework as filters
from django.forms import DateTimeInput
from .models import DatoProcesado
class DatosPreProcesadosFilter(filters.FilterSet):
    from_date = filters.filters.DateTimeFilter(field_name="date", lookup_expr="gte", widget=DateTimeInput(attrs=dict(type="datetime-local")))
    to_date = filters.filters.DateTimeFilter(field_name="date", lookup_expr="lte", widget=DateTimeInput(attrs=dict(type="datetime-local")))

    class Meta:
        model = DatoProcesado
        fields = ["fila"]