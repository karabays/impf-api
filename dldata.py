import requests
import datetime as dt
from pathlib import Path
import json
from collections import Counter
import csv

base_path = Path(__file__).parent.joinpath('data')
csv_path = base_path.joinpath('csv')

deliveries_timeseries_url = "https://impfdashboard.de/static/data/germany_deliveries_timeseries_v2.tsv"
vaccinations_timeseries_url = "https://impfdashboard.de/static/data/germany_vaccinations_timeseries_v2.tsv"
vaccinations_by_state_url = "https://impfdashboard.de/static/data/germany_vaccinations_by_state.tsv"


def save_file(url):
    file_name = url.rsplit('/', 1)[1]
    r = requests.get(url, allow_redirects=True)
    with open(csv_path.joinpath(file_name), 'wb') as f:
        f.write(r.content)
    return file_name


def load_states():
    csv_data = []
    with open(csv_path.joinpath("germany_states.csv"), 'r') as f:
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


def deliveries_timeseries(url):
    file_name = save_file(url)
    #file_name = "germany_deliveries_timeseries_v2.tsv"
    tsv_data = []
    with open(csv_path.joinpath(file_name), "r") as f:
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


def vaccinations_by_state(url):
    file_name = save_file(url)
    #file_name = "germany_vaccinations_by_state.tsv"
    tsv_data = []
    with open(csv_path.joinpath(file_name), "r") as f:
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


def vaccinations_timeseries(url):
    file_name = save_file(url)
    #file_name = "germany_vaccinations_timeseries_v2.tsv"
    total_tsv_data = []
    with open(csv_path.joinpath(file_name), "r") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader, None)
        for line in reader:
            total_tsv_data.append([line[1], line[8], line[9]])
        total_tsv_data = total_tsv_data[-1]
    vaccinations_total = {'vaccinationsTotal': int(total_tsv_data[0]), 
        'peopleFirstTotal': int(total_tsv_data[1]), 
        'peopleFullTotal': int(total_tsv_data[2])
        }
    return vaccinations_total


def metadata():
    metadata_json = requests.get("https://impfdashboard.de/static/data/metadata.json").json()
    now = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    metadata_json['lastChecked'] = now
    with open(base_path.joinpath('metadata.json'), 'w') as f:
        f.write(json.dumps(metadata_json, indent=2))
    return metadata_json


def save_json(data_dict):
    with open(base_path.joinpath('data.json'), 'w') as f:
        f.write(json.dumps(data_dict, indent=2))


def main():
    data_dict = {}
    deliveries = deliveries_timeseries(deliveries_timeseries_url)
    vaccinations = vaccinations_by_state(vaccinations_by_state_url)
    vaccinations["total"] = vaccinations_timeseries(vaccinations_timeseries_url)
    state_data = load_states()

    data_dict = {"vaccinations_by_state":vaccinations}
    for kode in vaccinations.keys():
        population = state_data[kode]['population']
        data_dict["vaccinations_by_state"][kode]["stateName"] = state_data[kode]['english-name']
        data_dict["vaccinations_by_state"][kode]["population"] = population
        data_dict["vaccinations_by_state"][kode]["vaccinationsPercent"] = round(vaccinations[kode]["vaccinationsTotal"]*100 / population, 1)
        data_dict["vaccinations_by_state"][kode]["peopleFirstPercent"] = round(vaccinations[kode]["peopleFirstTotal"]*100 / population, 1)
        data_dict["vaccinations_by_state"][kode]["peopleFullPercent"] = round(vaccinations[kode]["peopleFullTotal"]*100 / population, 1)
        data_dict["vaccinations_by_state"][kode]["vaccinesDelivered"] = deliveries[kode]

    data_dict["metadata"] = metadata()
    save_json(data_dict)


if __name__ == "__main__":
    main()