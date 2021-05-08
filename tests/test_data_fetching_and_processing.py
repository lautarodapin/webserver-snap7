from django.db.models.query import QuerySet
from django.dispatch.dispatcher import receiver
from app.tasks import fetch_data_from_plc, get_queryset_to_fetch, procesar_datos
from app.models import Area, Dato, DatoProcesado, Fila, Plc, end_fetching_data
from typing import List, Tuple
import unittest
import pytest
from django.test import TestCase
from snap7.server import mainloop
from multiprocessing import Process
import time
import snap7
import struct


ip = "127.0.0.1"
rack = 0
slot = 0
port = 1102


class TestDataFetchingAndProcessing(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.process = Process(target=mainloop)
        cls.process.start()
        time.sleep(2)  # wait for server to start

    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        cls.process.join(1)
        if cls.process.is_alive():
            cls.process.kill()

    def setUp(self):
        self.client : snap7.client.Client = snap7.client.Client()
        self.client.connect(ip, rack, slot, port)

        self.createBasicModels()        
        data = bytearray(10)
        data[0:0+2] = struct.pack(">h", 100)
        data[2:2+2] = struct.pack(">h", 230)
        data[4:4+2] = struct.pack(">h", 25)
        self.client.db_write(1, 0, data)

    def tearDown(self):
        self.client.disconnect()
        self.client.destroy()

    def createBasicModels(self):
        self.plc: Plc = Plc.objects.create(ip=ip, rack=rack, slot=slot, port=port, nombre="test plc")
        self.area: Area = Area.objects.create(plc=self.plc, area=Area.DB, nombre="area 1", numero=1, offset=10)
        self.fila_1: Fila = Fila.objects.create(area=self.area, name="fila 1", byte=0, tipo_dato=Fila.INT)
        self.fila_2: Fila = Fila.objects.create(area=self.area, name="fila 2", byte=2, tipo_dato=Fila.INT)
        self.fila_3: Fila = Fila.objects.create(area=self.area, name="fila 3", byte=4, tipo_dato=Fila.INT)

    def test_class(self):
        assert self.client.get_connected()
        data = self.client.db_read(1, 0, 6)
        assert 100 == snap7.util.get_int(data, 0)
        assert 230 == snap7.util.get_int(data, 2)
        assert 25 == snap7.util.get_int(data, 4)

    
    def test_get_queryset_to_fetch(self):
        queryset = get_queryset_to_fetch(ids=[self.area.pk])
        assert queryset[0].get("plc__ip") == ip
        assert queryset[0].get("numero") == 1
        assert queryset[0].get("offset") == 10
        assert queryset[0].get("area") == snap7.types.areas.DB


    def test_fetch_data_from_plc(self):
        fetch_data_from_plc(ids=[self.area.pk])

        dato = Dato.objects.first()
        assert dato
        assert snap7.util.get_int(dato.value, 0) == 100
        assert snap7.util.get_int(dato.value, 2) == 230
        assert snap7.util.get_int(dato.value, 4) == 25
        

    def test_procesar_datos(self):
        fetch_data_from_plc(ids=[self.area.pk])
        queryset = Dato.objects.all()
        assert queryset.exists()
        procesar_datos()
        assert queryset.first().procesado

        datos_procesados: List[DatoProcesado] = list(DatoProcesado.objects.all())
    
        assert datos_procesados[0].value == 100
        assert datos_procesados[1].value == 230
        assert datos_procesados[2].value == 25


    def test_end_fetching_data_signal(self):
        test = []
        @receiver(signal=end_fetching_data)
        def fire_process_data_after_fetching(sender, ids, **kwargs):
            test.append((sender, ids))

        fetch_data_from_plc(ids=[self.area.pk])

        assert test[0] == ("fetch_data_from_plc", [self.area.pk])
