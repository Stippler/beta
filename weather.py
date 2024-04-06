import pandas as pd
import requests
import json
from datetime import datetime, timedelta


SINGLE_LAYER = "https://climathon.iblsoft.com/data/gfs-0.5deg/edr/collections/single-layer"
TEMP_PARAM = "temperature_gnd-surf"
PERCIPATION_PARAM = "precipitation-rate_gnd-surf"
RAIN_BOOL_PARAM = "categorical-rain-yes-1-no-0_gnd-surf"
headers = {
    "accept": "application/json"
}

parameters = ['categorical-rain-yes-1-no-0_gnd-surf',
 'temperature_gnd-surf',
 'precipitation-rate_gnd-surf',
 'wind-speed-gust_gnd-surf',
 'sunshine-duration_gnd-surf',
 'visibility_gnd-surf',
 ]

possible_values=['categorical-rain-yes-1-no-0_gnd-surf',
 'categorical-freezing-rain-yes-1-no-0_gnd-surf',
 'categorical-ice-pellets-yes-1-no-0_gnd-surf',
 'categorical-snow-yes-1-no-0_gnd-surf',
 'land-cover_gnd-surf',
 'temperature_gnd-surf',
 'precipitation-rate_gnd-surf',
 'snow-depth_gnd-surf',
 'water-equivalent-of-accumulated-snow-depth_gnd-surf',
 'percent-frozen-precipitation_gnd-surf',
 'wind-speed-gust_gnd-surf',
 'frictional-velocity_gnd-surf',
 'pressure_gnd-surf',
 'geopotential-height_gnd-surf',
 'planetary-boundary-layer-height_gnd-surf',
 'sunshine-duration_gnd-surf',
 'convective-available-potential-energy_gnd-surf',
 'convective-inhibition_gnd-surf',
 'surface-lifted-index_gnd-surf',
 'best-4-layer-lifted-index_gnd-surf',
 'visibility_gnd-surf',
 'surface-roughness_gnd-surf',
 'vegetation_gnd-surf',
 'plant-canopy-surface-water_gnd-surf',
 'wilting-point_gnd-surf',
 'soil-type_gnd-surf',
 'field-capacity_gnd-surf',
 'haines-index_gnd-surf',
 'ice-cover_gnd-surf',
 'ice-thickness_gnd-surf']

FIVE_HOURS = timedelta(hours=5)

def extract_relevant_info(entry):
        date = entry['domain']['axes']['t']['values'][0]
        type = list(entry['ranges'].keys())[0]
        values = entry['ranges'][type]['values'][0]
        return {'time':convert_to_date(date),'parameter': type,'value': values}

def convert_to_date(date):
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")

def get_dates(from_date, to_date):
    url = f"https://climathon.iblsoft.com/data/gfs-0.5deg/edr/collections/single-layer"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            values = data['extent']['temporal']['values']
            values = list(map(lambda x: convert_to_date(x), values))
            return find_intersection(from_date, to_date, values)
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def find_intersection(from_date, to_date, values):
    intersection = []

    for value in values:
        if from_date <= value <= to_date:
                intersection.append(value)

    if len(intersection) == 0:
            # Find the closest values to the boundaries
        closest_to_from = min(values, key=lambda x: abs(x - from_date))
        closest_to_to = min(values, key=lambda x: abs(x - to_date))
        if abs(closest_to_from-from_date) < FIVE_HOURS:
            intersection.append(closest_to_from)
        if abs(closest_to_to-to_date) < FIVE_HOURS:
            intersection.append(closest_to_to)

        
    return intersection

def get_weather_data(x, y, from_date, to_date):
    date_values = get_dates(from_date, to_date)
    if len(date_values) == 0:
        print(f"Event is too far in the past or in the future")
        return None

    url = f"https://climathon.iblsoft.com/data/gfs-0.5deg/edr/collections/single-layer/position?coords=POINT({x}%20{y})&datetime={','.join(list(map(lambda x: x.strftime('%Y-%m-%dT%H:%M:%SZ'),date_values)))}&parameter-name={','.join(parameters)}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            entries =  list(map(lambda x: extract_relevant_info(x),response.json()['coverages']))
            # Convert the list of dictionaries to a DataFrame
            df = pd.DataFrame(entries)

            # Pivot the DataFrame
            df_pivot = df.pivot_table(index='time', columns='parameter', values='value', aggfunc='first')

            # Reset index to make 'time' a column again
            df_pivot.reset_index(inplace=True)
            return df_pivot
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    
