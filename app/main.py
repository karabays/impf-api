from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, validator
from collections import Counter
import csv
from pathlib import Path
import json

class Vaccination(BaseModel):
    '''Response model for the statistics.'''

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

data_folder = Path(__file__).parent.joinpath('../data')

app = FastAPI(title="impf-API",
    description="API to serve data from https://impfdashbaord.de",
    version="0.9.1",
)


def load_database():
    with open(data_folder.joinpath('data.json')) as f:
        data = json.load(f)
    return data


def get_metadata():
    return load_database()["metadata"]


def query_state(state_code):
    return load_database()["vaccinations_by_state"][state_code]


@app.get('/')
def index():
    """Return the metadata."""
    return get_metadata()


@app.get("/total/", response_model=Vaccination)
def total_data():
    """Return country total statistics."""
    result =  query_state("total")
    return result


@app.get("/states/", response_model=Vaccination)
def state_data(state_code: str = Query(..., min_length=2, max_length=2)):
    """Return state statistics. Requires a querry paramater to
    be passed with 2 digit state code.

    ?state_code=hh
    """
    if state_code in state_list:
        result =  query_state("de-"+state_code)
        return result
    else:
        raise HTTPException(404, detail='Invalid state code.')