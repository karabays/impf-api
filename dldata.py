from pydantic.types import Json
import requests
import datetime as dt
from pathlib import Path
import json

base_path = Path(__file__).parent.joinpath('data')

deliveries_timeseries = "https://impfdashboard.de/static/data/germany_deliveries_timeseries_v2.tsv"
vaccinations_timeseries = "https://impfdashboard.de/static/data/germany_vaccinations_timeseries_v2.tsv"
vaccinations_by_state = "https://impfdashboard.de/static/data/germany_vaccinations_by_state.tsv"


def save_file(url):
    file_name = url.rsplit('/', 1)[1]
    r = requests.get(url, allow_redirects=True)
    with open(base_path.joinpath(file_name), 'wb') as f:
        f.write(r.content)


def metadata():
    metadata_json = requests.get("https://impfdashboard.de/static/data/metadata.json").json()
    now = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    metadata_json['lastChecked'] = now
    with open(base_path.joinpath('metadata.json'), 'w') as f:
        f.write(json.dumps(metadata_json, indent=2))

save_file(deliveries_timeseries)
save_file(vaccinations_timeseries)
save_file(vaccinations_by_state)
metadata()