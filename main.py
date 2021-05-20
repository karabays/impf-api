from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, validator
from collections import Counter
import csv

class Vaccination(BaseModel):
    vaccinationsTotal: int
    peopleFirstTotal: int
    peopleFullTotal: int
    stateName: str
    population: int
    vaccinationsPercent: int
    peopleFirstPercent: float
    peopleFullPercent: float
    vaccinesDelivered: float


state_list = ['bb','be','nd','bw','by','hb','he','hh',
         'mv','ni','nw','rp','sh','sl','sn','st','th']


app = FastAPI()


def load_states():
    csv_data = []
    with open('germany_states.csv', 'r') as f:
        for line in csv.DictReader(f):
            csv_data.append(line)
    germany_states = {}
    for i in csv_data:
        code = i.pop('code', None).lower()
        germany_states[code] = i
        germany_states[code]['population'] = int(germany_states[code]['population'])
    return germany_states


def load_state_data():
    tsv_data = []
    with open("germany_vaccinations_by_state.tsv", "r") as f:
        for line in csv.DictReader(f, delimiter="\t"):
            for key in line.keys():
                if line[key].isdigit():
                    line[key]=int(line[key])
            tsv_data.append(line)

    vaccinations_by_state = {}
    for i in tsv_data:
        code = i.pop('code', None).lower()
        vaccinations_by_state[code] = i
    return vaccinations_by_state


def load_delivery_data():
    tsv_data = []
    with open("germany_deliveries_timeseries_v2.tsv", "r") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader, None)
        for line in reader:
            tsv_data.append({line[2].lower():int(line[3])})
    c = Counter()
    for l in tsv_data:
        c.update(l)
    return dict(c)


def consolidate_data():
    states_data = load_states()
    delivery_data = load_delivery_data()
    vaccinations_by_state = load_state_data()
    for kode in vaccinations_by_state.keys():
        vaccinations_by_state[kode]["stateName"] = states_data[kode]['english-name']
        vaccinations_by_state[kode]["population"] = states_data[kode]['population']
        vaccinations_by_state[kode]["vaccinationsPercent"] = round(vaccinations_by_state[kode]["vaccinationsTotal"]*100 / states_data[kode]['population'],1)
        vaccinations_by_state[kode]["peopleFirstPercent"] = round(vaccinations_by_state[kode]["peopleFirstTotal"]*100 / states_data[kode]['population'],1)
        vaccinations_by_state[kode]["peopleFullPercent"] = round(vaccinations_by_state[kode]["peopleFullTotal"]*100 / states_data[kode]['population'],1)
        vaccinations_by_state[kode]["vaccinesDelivered"] = delivery_data[kode]
    return vaccinations_by_state


@app.get("/states/", response_model=Vaccination)
def state_data(state_code: str = Query(..., min_length=2, max_length=2)):
    if state_code in state_list:
        result =  consolidate_data()["de-"+state_code]
        return result
    else:
        raise HTTPException(404, detail='Invalid state code.')