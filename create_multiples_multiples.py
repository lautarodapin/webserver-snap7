from dataclasses import dataclass, Field, asdict
from datetime import datetime, timedelta
import random
import json

@dataclass
class Fields:
    dato:str
    date:str
    name:str
    fila:int
    area:int = 1
    plc:int= 1
    raw_dato:int = 1
    created_at:str = "2020-01-01T00:00:00+00:00"
    mod_at:str="2020-01-01T00:00:00+00:00"

@dataclass
class Instance:
    fields: Fields
    pk:int
    model:str

if __name__ == "__main__":
    now = datetime.now()
    saved_now = now
    datos = []

    datos += [
        {"model": "app.plc", "pk": 1, "fields": {"ip": "127.0.0.1", "rack": 0, "slot": 0, "port": 1012, "mod_at": "2020-01-01T00:00:00+00:00", "created_at": "2020-01-01T00:00:00+00:00"}},
        {"model": "app.area", "pk": 1, "fields": {"plc": 1, "nombre": "area", "area": 132, "numero": 1, "offset": 2, "created_at": "2020-01-01T00:00:00+00:00", "mod_at": "2020-01-01T00:00:00+00:00"}},
        {"model": "app.area", "pk": 2, "fields": {"plc": 1, "nombre": "area", "area": 132, "numero": 2, "offset": 2, "created_at": "2020-01-01T00:00:00+00:00", "mod_at": "2020-01-01T00:00:00+00:00"}},
    ]

    datos += [
    {"model": "app.fila", "pk": 1, "fields": {"area": 1, "name": "entero 1", "byte": 0, "bit": 0, "tipo_dato": "get_int", "created_at": "2020-01-01T00:00:00+00:00", "mod_at": "2020-01-01T00:00:00+00:00"}},
    {"model": "app.fila", "pk": 2, "fields": {"area": 1, "name": "booleano 1", "byte": 2, "bit": 0, "tipo_dato": "get_bool", "created_at": "2020-01-01T00:00:00+00:00", "mod_at": "2020-01-01T00:00:00+00:00"}},
    {"model": "app.fila", "pk": 3, "fields": {"area": 1, "name": "float 1", "byte": 3, "bit": 0, "tipo_dato": "get_real", "created_at": "2020-01-01T00:00:00+00:00", "mod_at": "2020-01-01T00:00:00+00:00"}},
    {"model": "app.fila", "pk": 4, "fields": {"area": 1, "name": "entero 2", "byte": 3, "bit": 0, "tipo_dato": "get_real", "created_at": "2020-01-01T00:00:00+00:00", "mod_at": "2020-01-01T00:00:00+00:00"}},
    {"model": "app.fila", "pk": 5, "fields": {"area": 1, "name": "booleano 2", "byte": 3, "bit": 0, "tipo_dato": "get_real", "created_at": "2020-01-01T00:00:00+00:00", "mod_at": "2020-01-01T00:00:00+00:00"}},
    {"model": "app.fila", "pk": 6, "fields": {"area": 1, "name": "float 2", "byte": 3, "bit": 0, "tipo_dato": "get_real", "created_at": "2020-01-01T00:00:00+00:00", "mod_at": "2020-01-01T00:00:00+00:00"}},
    {"model": "app.fila", "pk": 7, "fields": {"area": 1, "name": "entero 3", "byte": 3, "bit": 0, "tipo_dato": "get_real", "created_at": "2020-01-01T00:00:00+00:00", "mod_at": "2020-01-01T00:00:00+00:00"}},
    {"model": "app.fila", "pk": 8, "fields": {"area": 1, "name": "booleano 3", "byte": 3, "bit": 0, "tipo_dato": "get_real", "created_at": "2020-01-01T00:00:00+00:00", "mod_at": "2020-01-01T00:00:00+00:00"}},
    {"model": "app.fila", "pk": 9, "fields": {"area": 1, "name": "float 3", "byte": 3, "bit": 0, "tipo_dato": "get_real", "created_at": "2020-01-01T00:00:00+00:00", "mod_at": "2020-01-01T00:00:00+00:00"}},    
    ]

    for i in range(100000):
        now += timedelta(seconds=1)
        date = f"{now.year}-{now.month}-{now.day}T{now.hour}:{now.minute}:{now.second}+00:00"
        fields = Fields(dato=f"int:{random.randint(0, 100)}", date=date, name="entero 1", fila=1)
        instance = Instance(fields=fields, pk=i+1, model="app.datoprocesado")
        datos.append(asdict(instance))
    now = saved_now
    for i in range(100000):
        now += timedelta(seconds=1)
        date = f"{now.year}-{now.month}-{now.day}T{now.hour}:{now.minute}:{now.second}+00:00"
        fields = Fields(dato=f"float:{random.uniform(0, 100)}", date=date, name="real 1", fila=3)
        instance = Instance(fields=fields, pk=i+1+100000, model="app.datoprocesado")
        datos.append(asdict(instance))
    now = saved_now
    for i in range(100000):
        now += timedelta(seconds=1)
        date = f"{now.year}-{now.month}-{now.day}T{now.hour}:{now.minute}:{now.second}+00:00"
        r = random.choice(["True", "False"])
        fields = Fields(dato=f"bool:{r}", date=date, name="booleano 1", fila=2)
        instance = Instance(fields=fields, pk=i+1+(100000*2), model="app.datoprocesado")
        datos.append(asdict(instance))


    for i in range(100000):
        now += timedelta(seconds=1)
        date = f"{now.year}-{now.month}-{now.day}T{now.hour}:{now.minute}:{now.second}+00:00"
        fields = Fields(dato=f"int:{random.randint(0, 100)}", date=date, name="entero 2", fila=4)
        instance = Instance(fields=fields, pk=i+1+(100000*3), model="app.datoprocesado")
        datos.append(asdict(instance))
    now = saved_now
    for i in range(100000):
        now += timedelta(seconds=1)
        date = f"{now.year}-{now.month}-{now.day}T{now.hour}:{now.minute}:{now.second}+00:00"
        fields = Fields(dato=f"float:{random.uniform(0, 100)}", date=date, name="real 2", fila=6)
        instance = Instance(fields=fields, pk=i+1+(100000*4), model="app.datoprocesado")
        datos.append(asdict(instance))
    now = saved_now
    for i in range(100000):
        now += timedelta(seconds=1)
        date = f"{now.year}-{now.month}-{now.day}T{now.hour}:{now.minute}:{now.second}+00:00"
        r = random.choice(["True", "False"])
        fields = Fields(dato=f"bool:{r}", date=date, name="booleano 2", fila=5)
        instance = Instance(fields=fields, pk=i+1+(100000*5), model="app.datoprocesado")
        datos.append(asdict(instance))
    for i in range(100000):
        now += timedelta(seconds=1)
        date = f"{now.year}-{now.month}-{now.day}T{now.hour}:{now.minute}:{now.second}+00:00"
        fields = Fields(dato=f"int:{random.randint(0, 100)}", date=date, name="entero 3", fila=7)
        instance = Instance(fields=fields, pk=i+1+(100000*6), model="app.datoprocesado")
        datos.append(asdict(instance))
    now = saved_now
    for i in range(100000):
        now += timedelta(seconds=1)
        date = f"{now.year}-{now.month}-{now.day}T{now.hour}:{now.minute}:{now.second}+00:00"
        fields = Fields(dato=f"float:{random.uniform(0, 100)}", date=date, name="real 3", fila=9)
        instance = Instance(fields=fields, pk=i+1+(100000*7), model="app.datoprocesado")
        datos.append(asdict(instance))
    now = saved_now
    for i in range(100000):
        now += timedelta(seconds=1)
        date = f"{now.year}-{now.month}-{now.day}T{now.hour}:{now.minute}:{now.second}+00:00"
        r = random.choice(["True", "False"])
        fields = Fields(dato=f"bool:{r}", date=date, name="booleano 3", fila=8)
        instance = Instance(fields=fields, pk=i+1+(100000*8), model="app.datoprocesado")
        datos.append(asdict(instance))

    with open("test.json", "w") as f:
        json.dump(datos, f)