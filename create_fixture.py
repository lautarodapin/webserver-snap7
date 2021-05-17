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

    with open("test.json", "w") as f:
        json.dump(datos, f)