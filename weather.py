import pandas as pd
import requests
import json
from datetime import datetime, timedelta

headers = {
    "accept": "application/json"
}

#HEIGHT_ABOVE_GROUND_2 = "https://climathon.iblsoft.com/data/gfs-0.5deg/edr/collections"
#HEIGHT_ABOVE_GROUND_2_PARAMS ={
#    "maximum-temperature_stat:max/PT3H": "Maximum temperature - Maximum 3h",
#    "minimum-temperature_stat:min/PT3H": "Minimum temperature - Minimum 3h"
#}

# medium range 3h
SINGLE_LAYER_2 = "https://climathon.iblsoft.com/data/gfs-0.5deg/edr/collections"
SINGLE_LAYER_2_PARAMETERS = {
    "latent-heat-net-flux_gnd-surf_stat:avg/PT3H": "Latent heat net flux - Ground surface - Average 3h",
    "sensible-heat-net-flux_gnd-surf_stat:avg/PT3H": "Sensible heat net flux - Ground surface - Average 3h",
    "precipitation-rate_gnd-surf_stat:avg/PT3H": "Precipitation rate - Ground surface - Average 3h",
    "total-precipitation_gnd-surf_stat:acc/PT3H": "Total precipitation - Ground surface - Accumulation 3h",
    "convective-precipitation_gnd-surf_stat:acc/PT3H": "Convective precipitation - Ground surface - Accumulation 3h",
    "categorical-rain-yes-1-no-0_gnd-surf_stat:avg/PT3H": "Categorical rain (yes=1; no=0) - Ground surface - Average 3h",
    "categorical-freezing-rain-yes-1-no-0_gnd-surf_stat:avg/PT3H": "Categorical freezing rain (yes=1; no=0) - Ground surface - Average 3h",
    "categorical-ice-pellets-yes-1-no-0_gnd-surf_stat:avg/PT3H": "Categorical ice pellets (yes=1; no=0) - Ground surface - Average 3h",
    "categorical-snow-yes-1-no-0_gnd-surf_stat:avg/PT3H": "Categorical snow (yes=1; no=0) - Ground surface - Average 3h",
    "convective-precipitation-rate_gnd-surf_stat:avg/PT3H": "Convective precipitation rate - Ground surface - Average 3h",
    "momentum-flux-u-component_gnd-surf_stat:avg/PT3H": "Momentum flux, U component - Ground surface - Average 3h",
    "momentum-flux-v-component_gnd-surf_stat:avg/PT3H": "Momentum flux, V component - Ground surface - Average 3h",
    "zonal-flux-of-gravity-wave-stress_gnd-surf_stat:avg/PT3H": "Zonal flux of gravity wave stress - Ground surface - Average 3h",
    "meridional-flux-of-gravity-wave-stress_gnd-surf_stat:avg/PT3H": "Meridional flux of gravity wave stress - Ground surface - Average 3h",
    "downward-short-wave-radiation-flux_gnd-surf_stat:avg/PT3H": "Downward short-wave radiation flux - Ground surface - Average 3h",
    "upward-short-wave-radiation-flux_gnd-surf_stat:avg/PT3H": "Upward short-wave radiation flux - Ground surface - Average 3h",
    "downward-long-wave-radiation-flux_gnd-surf_stat:avg/PT3H": "Downward long-wave radiation flux - Ground surface - Average 3h",
    "upward-long-wave-radiation-flux_gnd-surf_stat:avg/PT3H": "Upward long-wave radiation flux - Ground surface - Average 3h",
    "albedo_gnd-surf_stat:avg/PT3H": "Albedo - Ground surface - Average 3h",
    "water-runoff_gnd-surf_stat:acc/PT3H": "Water runoff - Ground surface - Accumulation 3h",
    "ground-heat-flux_gnd-surf_stat:avg/PT3H": "Ground heat flux - Ground surface - Average 3h"
}
# long range 6h
SINGLE_LAYER_3 = "https://climathon.iblsoft.com/data/gfs-0.5deg/edr/collections"
SINGLE_LAYER_3_PARAMETERS={
    "latent-heat-net-flux_gnd-surf_stat:avg/PT6H": "Latent heat net flux - Ground surface - Average 6h",
    "sensible-heat-net-flux_gnd-surf_stat:avg/PT6H": "Sensible heat net flux - Ground surface - Average 6h",
    "precipitation-rate_gnd-surf_stat:avg/PT6H": "Precipitation rate - Ground surface - Average 6h",
    "total-precipitation_gnd-surf_stat:acc/PT6H": "Total precipitation - Ground surface - Accumulation 6h",
    "convective-precipitation_gnd-surf_stat:acc/PT6H": "Convective precipitation - Ground surface - Accumulation 6h",
    "categorical-rain-yes-1-no-0_gnd-surf_stat:avg/PT6H": "Categorical rain (yes=1; no=0) - Ground surface - Average 6h",
    "categorical-freezing-rain-yes-1-no-0_gnd-surf_stat:avg/PT6H": "Categorical freezing rain (yes=1; no=0) - Ground surface - Average 6h",
    "categorical-ice-pellets-yes-1-no-0_gnd-surf_stat:avg/PT6H": "Categorical ice pellets (yes=1; no=0) - Ground surface - Average 6h",
    "categorical-snow-yes-1-no-0_gnd-surf_stat:avg/PT6H": "Categorical snow (yes=1; no=0) - Ground surface - Average 6h",
    "convective-precipitation-rate_gnd-surf_stat:avg/PT6H": "Convective precipitation rate - Ground surface - Average 6h",
    "momentum-flux-u-component_gnd-surf_stat:avg/PT6H": "Momentum flux, U component - Ground surface - Average 6h",
    "momentum-flux-v-component_gnd-surf_stat:avg/PT6H": "Momentum flux, V component - Ground surface - Average 6h",
    "zonal-flux-of-gravity-wave-stress_gnd-surf_stat:avg/PT6H": "Zonal flux of gravity wave stress - Ground surface - Average 6h",
    "meridional-flux-of-gravity-wave-stress_gnd-surf_stat:avg/PT6H": "Meridional flux of gravity wave stress - Ground surface - Average 6h",
    "downward-short-wave-radiation-flux_gnd-surf_stat:avg/PT6H": "Downward short-wave radiation flux - Ground surface - Average 6h",
    "upward-short-wave-radiation-flux_gnd-surf_stat:avg/PT6H": "Upward short-wave radiation flux - Ground surface - Average 6h",
    "downward-long-wave-radiation-flux_gnd-surf_stat:avg/PT6H": "Downward long-wave radiation flux - Ground surface - Average 6h",
    "upward-long-wave-radiation-flux_gnd-surf_stat:avg/PT6H": "Upward long-wave radiation flux - Ground surface - Average 6h",
    "albedo_gnd-surf_stat:avg/PT6H": "Albedo - Ground surface - Average 6h",
    "water-runoff_gnd-surf_stat:acc/PT6H": "Water runoff - Ground surface - Accumulation 6h",
    "ground-heat-flux_gnd-surf_stat:avg/PT6H": "Ground heat flux - Ground surface - Average 6h"
}


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

    url = f"https://climathon.iblsoft.com/data/gfs-0.5deg/edr/collections/single-layer/position?coords=POINT({x}%20{y})&datetime={','.join(list(map(lambda x: x.strftime('%Y-%m-%dT%H:%M:%SZ'),date_values)))}"#&parameter-name={','.join(parameters)}"
    
    try:
        response = requests.get(url)
        # Specify the file path
        file_path = "output.txt"

        # Open the file in write mode and write the string to it
        with open(file_path, 'w') as file:
            file.write(json.dumps(response.json()))
        print(response.json())
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
    
