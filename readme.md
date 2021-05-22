# impf-api

URL: http://www.impf-api.xyz/

API Docs: http://www.impf-api.xyz/docs


A simple api to serve data from https://impfdashboard.de/ built with FastAPI.

## Deploy

### Running

    uvicorn app.main:app

### Data Update

Cron job to check data periodically.

    46 * * * * python3 /home/ubuntu/impf-api/dldata.py >/dev/null 2>&1

## API Reference

Really simple api with 3 endpoints. 

For States, send a query with 2 digit state_code.

| State Code | Name                   |
|------------|------------------------|
| BW         | Baden-Württemberg      |
| BY         | Bayern                 |
| BE         | Berlin                 |
| BB         | Brandenburg            |
| HB         | Bremen                 |
| HH         | Hamburg                |
| HE         | Hessen                 |
| MV         | Mecklenburg-Vorpommern |
| NI         | Niedersachsen          |
| NW         | Nordrhein-Westfalen    |
| RP         | Rheinland-Pfalz        |
| SL         | Saarland               |
| SN         | Sachsen                |
| ST         | Sachsen-Anhalt         |
| SH         | Schleswig-Holstein     |
| TH         | Thüringen              |

For testing and more information http://www.impf-api.xyz/docs