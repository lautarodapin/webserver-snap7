from django_filters import rest_framework as filters
from .models import DatoProcesado

class DatosPreProcesadosFilter(filters.FilterSet):
    from_date = filters.filters.DateTimeFilter(field_name="date", lookup_expr="gte")
    to_date = filters.filters.DateTimeFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = DatoProcesado
        fields = ["date", "fila"]