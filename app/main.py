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
    vaccinationsPercent: float
    peopleFirstPercent: float
    peopleFullPercent: float
    vaccinesDelivered: int


state_list = ['bb','be','nd','bw','by','hb','he','hh',
         'mv','ni','nw','rp','sh','sl','sn','st','th']


app = FastAPI()


def load_states():
    csv_data = []
    with open('./app/germany_states.csv', 'r') as f:
        for line in csv.DictReader(f):
            csv_data.append(line)
    germany_states = {}
    for i in csv_data:
        code = i.pop('code', None).lower()
        germany_states[code] = i
        germany_states[code]['population'] = int(germany_states[code]['population'])
    germany_states_list = list(germany_states.values())
    total_population = sum([i['population'] for i in germany_states_list])
    germany_states['total'] = {'population':total_population,
        'english-name': 'Germany Total'}
    return germany_states


def load_state_data():
    tsv_data = []
    with open("./app/germany_vaccinations_by_state.tsv", "r") as f:
        for line in csv.DictReader(f, delimiter="\t"):
            for key in line.keys():
                if line[key].isdigit():
                    line[key]=int(line[key])
            tsv_data.append(line)
    vaccinations_by_state = {}
    for i in tsv_data:
        code = i.pop('region', None).lower()
        vaccinations_by_state[code] = i

    total_tsv_data = []
    with open("./app/germany_vaccinations_timeseries_v2.tsv", "r") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader, None)
        for line in reader:
            total_tsv_data.append([line[1], line[8], line[9]])
        total_tsv_data = total_tsv_data[-1]
    
    vaccinations_by_state['total'] = {'vaccinationsTotal': int(total_tsv_data[0]), 
        'peopleFirstTotal': int(total_tsv_data[1]), 
        'peopleFullTotal': int(total_tsv_data[2])}
    
    return vaccinations_by_state


def load_delivery_data():
    tsv_data = []
    with open("./app/germany_deliveries_timeseries_v2.tsv", "r") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader, None)
        for line in reader:
            tsv_data.append({line[2].lower():int(line[3])})
    c = Counter()
    for l in tsv_data:
        c.update(l)
    delivery_data = dict(c)
    delivery_data['total'] = sum(delivery_data.values())
    
    return delivery_data


def consolidate_data(code):
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
    return vaccinations_by_state[code]


@app.get("/total/", response_model=Vaccination)
def total_data():
    result =  consolidate_data("total")
    return result


@app.get("/states/", response_model=Vaccination)
def state_data(state_code: str = Query(..., min_length=2, max_length=2)):
    if state_code in state_list:
        result =  consolidate_data("de-"+state_code)
        return result
    else:
        raise HTTPException(404, detail='Invalid state code.')

