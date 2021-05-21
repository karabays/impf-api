import requests

deliveries_timeseries = "https://impfdashboard.de/static/data/germany_deliveries_timeseries_v2.tsv"
vaccinations_timeseries = "https://impfdashboard.de/static/data/germany_vaccinations_timeseries_v2.tsv"
vaccinations_by_state = "https://impfdashboard.de/static/data/germany_vaccinations_by_state.tsv"


def save_file(url):
    file_name = url.rsplit('/', 1)[1]
    r = requests.get(url, allow_redirects=True)
    with open("app/"+file_name, 'wb') as f:
        f.write(r.content)

save_file(deliveries_timeseries)
save_file(vaccinations_timeseries)
save_file(vaccinations_by_state)