import pandas as pd
import requests
import json
from datetime import datetime, timedelta
from openai import OpenAI
from dotenv import load_dotenv
import os

headers = {
    "accept": "application/json"
}

#HEIGHT_ABOVE_GROUND_2 = "https://climathon.iblsoft.com/data/gfs-0.5deg/edr/collections"
#HEIGHT_ABOVE_GROUND_2_PARAMS ={
#    "maximum-temperature_stat:max/PT3H": "Maximum temperature - Maximum 3h",
#    "minimum-temperature_stat:min/PT3H": "Minimum temperature - Minimum 3h"
#}

# OpenAI API variables

model = "gpt-4-1106-preview"
load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

question = "I want to go surfing tomorrow. Is this a good idea?"

# medium range 3h
SINGLE_LAYER_2 = "https://climathon.iblsoft.com/data/gfs-0.5deg/edr/collections/single-layer_2"
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
SINGLE_LAYER_3 = "https://climathon.iblsoft.com/data/gfs-0.5deg/edr/collections/single-layer_3"

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

def extract_relevant_info(entry):
        date = entry['domain']['axes']['t']['values'][0]
        type = list(entry['ranges'].keys())[0]
        values = entry['ranges'][type]['values'][0]
        return {'time':convert_to_date(date),'parameter': type,'value': values}

def convert_to_date(date):
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")

def get_dates(from_date, url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            values = data['extent']['temporal']['values']
            values = list(map(lambda x: convert_to_date(x), values))
            if from_date < values[0]:
                raise Exception('Event has already started')
            return find_first_value_less_than_or_equal_to_date(from_date, values)
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def find_first_value_less_than_or_equal_to_date(date, value_list):
    previous_element = value_list[0]
    for value in value_list[1:]:
        if value <= date:
            previous_element = value
        else:
            return previous_element
    raise Exception('Unexpected error')

def get_weather_data(x, y, from_date, to_date):
    duration = abs(to_date-from_date)
    url = None
    if duration <= timedelta(hours=3):
        url = SINGLE_LAYER_2
        parameters = SINGLE_LAYER_2_PARAMETERS
    else:
        url = SINGLE_LAYER_3
        parameters = SINGLE_LAYER_3_PARAMETERS

    date_value = get_dates(from_date, url)

    completion = client.chat.completions.create(
      model=model,
      response_format={ "type": "json_object" },
      messages=[
        {"role": "system", "content": "You are an expert in predicting how good an activity is based on the weather forecast. You receive a question about a planned activity and a list of parameters that you could get. Decide based on the activity which parameters you require from the list to answer the query. Make sure to only answer parameters that appear in the list. You return a json list of parameters that you need to answer the question in this form: {required_parameters: [parameter1, parameter2, ...]}" },
        {"role": "user", "content": f"{question}"},
        {"role": "system", "content": f"The list of parameters is: {parameters}"}
      ]
    )

    completion_message_content = completion.choices[0].message.content

    extracted_json = json.loads(completion_message_content)

    parameters= extracted_json['required_parameters']

    params = {
        'coords': f'POINT({y} {x})',
        'datetime': date_value.strftime('%Y-%m-%dT%H:%M:%SZ'),
    }

    try:
        # Sending a GET request with parameters
        response = requests.get(url + '/position', params=params)
        if response.status_code == 200:
            #response = requests.get(url)
            temp =  response.json()
            gen_info = temp['parameters']
            values = list(map(lambda x: x['ranges'],temp['coverages']))
            values = {list(value.keys())[0]:list(value.values())[0] for value in values}
            return {param: {'unit':gen_info[param]['unit']['symbol'], 'description':gen_info[param]['observedProperty']['label']['en'], 'value': values[param]['values'][0]} for param in parameters}
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    
