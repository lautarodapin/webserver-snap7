from dataclasses import dataclass, Field, asdict
from datetime import datetime, timedelta
import random
import json

@dataclass
class Fields:
    dato:str
    date:str
    name:str
    area:int = 1
    fila:int = 1
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
    datos = []
    for i in range(1000000):
        now += timedelta(seconds=1)
        date = f"{now.year}-{now.month}-{now.day}T{now.hour}:{now.minute}:{now.second}+00:00"
        fields = Fields(dato=f"int:{random.randint(0, 100)}", date=date, name="entero 1")
        instance = Instance(fields=fields, pk=i+1, model="app.datoprocesado")
        datos.append(asdict(instance))

    with open("test.json", "w") as f:
        json.dump(datos, f)