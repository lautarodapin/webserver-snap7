from django.db import models
from django.http import Http404
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist, ValidationError, FieldDoesNotExist, EmptyResultSet
from django.utils.translation import gettext as _
from django.utils.timezone import now
from django.utils.functional import cached_property
import logging

from django.core.cache import cache

import pandas as pd
import numpy as np
from django.template.defaultfilters import slugify

from snap7.client import Client
from snap7 import types as s7types
from snap7 import util as s7util

logger = logging.getLogger(__name__)

class Tag(models.Model):
    nombre = models.CharField(_("Nombre"), max_length=50)
    slug = models.SlugField(_("Slug"), editable=False, null=True)
    
    def __str__(self):
        return self.nombre

    def save(self):
        self.slug = slugify(f"{self.nombre}-{self.pk}" )
        super().save()
        
class Plc(models.Model):
    ip = models.GenericIPAddressField(_("IP"), unique=True)
    rack = models.PositiveSmallIntegerField(_("Rack"), blank=True)
    slot = models.PositiveSmallIntegerField(_("Slot"), blank=True)
    port = models.PositiveSmallIntegerField(_("Port"), blank=True, default=102)
    nombre = models.CharField(_("Nombre"), max_length=50, null=True, blank=True, help_text="Nombre alias")

    def __str__(self) -> str:
        return "%s:\t%s" % (self.nombre, self.ip)

    def client(self) -> Client:
        plc: Client = Client()
        plc.connect(self.ip, self.rack, self.slot, self.port)
        return plc
        
class Area(models.Model):
    class Meta:
        unique_together = ('area', 'numero', 'plc',)

    PE = s7types.S7AreaPE
    PA = s7types.S7AreaPA
    MK = s7types.S7AreaMK
    DB = s7types.S7AreaDB
    CT = s7types.S7AreaCT
    TM = s7types.S7AreaTM
    AREAS = (
        (PE, 'Entrada'),
        (PA, 'Salida'),
        (MK, 'Marca'),
        (DB, 'DB'),
        (CT, 'Contador'),
        (TM, 'Timer'),
    )
    plc: Plc = models.ForeignKey(Plc, verbose_name=_("PLC"), on_delete=models.CASCADE, related_name='areas')
    tag = models.ManyToManyField(Tag, verbose_name=_("Tag"), related_name="areas", blank=True)

    nombre = models.CharField(_("Nombre"), max_length=255)
    area = models.PositiveSmallIntegerField(_("Area"), choices=AREAS)
    numero = models.PositiveSmallIntegerField(_("Numero"), help_text="En el caso de E/M/A el numero debe ser 0")
    offset = models.PositiveSmallIntegerField(_("Offset"), null=False, blank=False, help_text="Maximo offset del area a leer")

    created_at = models.DateTimeField(_("Creado"), auto_now_add=True)
    mod_at = models.DateTimeField(_("Modificado"), auto_now=True)
    
    def __str__(self):
        return f"Area {self.get_area_display()} {self.numero} del plc {self.plc}"

    def read_from_plc(self) -> bytearray:
        plc = self.plc.client()
        return plc.read_area(self.area, self.numero, 0, self.offset)
        
    @cached_property
    def dataframe(self):
        datos = self.datos.all().values("created_at", "dato")


class Fila(models.Model):
    BOOL = 'get_bool'
    REAL = 'get_real'
    INT = 'get_int'
    DWORD = 'get_dword'

    TIPOS = (
        (BOOL, 'Bool (1 bit)'),
        (REAL, 'Real (4 bytes)'),
        (INT, 'Int (2 bytes)'),
        (DWORD, 'Double Word (4 bytes)'),
    )
    area = models.ForeignKey(Area, verbose_name=_("Area (DB)"), on_delete=models.CASCADE, related_name='filas', help_text="DB desde el cual se lee")
    name = models.CharField(max_length = 100, verbose_name=_("Nombre"))
    byte = models.PositiveSmallIntegerField(verbose_name=_("Byte"))
    bit = models.PositiveSmallIntegerField(verbose_name=_("Bit"), help_text="Es requerido si el tipo de dato es `Bool`", blank=True, null=True)
    tipo_dato = models.CharField(verbose_name=_("Tipo de dato"), choices=TIPOS, default=BOOL, help_text="Tipo de dato a leer", max_length=150)
    
    def __str__(self):
        return "{}\t{}\ttipo={}\tbyte={}\tbit={}".format(self.name, self.area, self.get_tipo_dato_display(), self.byte, self.bit or 0)
    
    def clean(self):
        # No permite que se añadan BIT sin colocar BIT
        if self.tipo_dato == self.BOOL and self.bit is None:
            raise ValidationError({
                'bit':ValidationError(
                    _("El tipo de dato %(value)s requiere que se coloque si o si el bit"), 
                    params={'value':self.get_tipo_dato_display()}
                    ),
            })
        if self.tipo_dato != self.BOOL:
            self.bit = 0
  
    def read_value(self, db=None):
        ''' Lee el valor segun el tipo de dato, del valor almacenado ene l padre '''
        bytearray_ = bytearray(db) ## si le paso un parametro utilizo ese parametro de lo contrario uso el de la lectura
        kwargs = {'byte_index':self.byte, 'bytearray_':bytearray_}
        if self.tipo_dato == self.BOOL: #en caso de no ser booleano no usa bool index
            kwargs['bool_index'] = self.bit
        return getattr(s7util, self.tipo_dato)(**kwargs)


class DatoAlmacenadoQuerySet(models.QuerySet):

    @cached_property
    def dataframe(self):
        queryset = self
        nombres = queryset.last().nombres # nombres de cada dato
        if not nombres:
            raise EmptyResultSet()
        tabla = [dato.read_valores for dato in queryset]
        x = [dato.created_at for dato in queryset]
        df = pd.DataFrame(tabla, columns=nombres)
        df['date'] = x
        for col in df.columns: # esto convierte los True en 1 y false en 0
            if df[col].dtype == np.dtype('bool'):
                df[col] = df.apply(lambda x: 1 if x[col] else 0, axis=1)
        return df

class DatoAlmacenadoManager(models.Manager):
    def get_queryset(self):
        return DatoAlmacenadoQuerySet(self.model)

class Dato(models.Model):
    class Meta:
        ordering = ["-created_at"]
    objects = models.Manager()
    custom_manager = DatoAlmacenadoManager()
    area = models.ForeignKey(Area, verbose_name=_("Area"), on_delete=models.CASCADE, null=False, related_name="datos")
    created_at = models.DateTimeField(_("Creado"), auto_now_add=True)
    mod_at = models.DateTimeField(_("Modificado"), auto_now=True)
    dato = models.BinaryField(_("Valor"), null=True, blank=True, max_length=65536, editable=True)

    @cached_property
    def read_valores(self):
        valores = self.lectura.valor_db.all() # * Busco todos los valores, relacionados con la lectura (Es decir las variables del DB)
        if valores.exists(): #
            return [valor.read_value(db=self.dato) for valor in valores] # * Para cada variable 
        return []

    @cached_property
    def nombres(self):
        valores = self.lectura.valor_db.all() 
        return [valor.name for valor in valores.all()] if valores.exists() else []  