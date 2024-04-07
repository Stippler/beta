import requests
import json
from datetime import datetime, timedelta
from openai import OpenAI
from dotenv import load_dotenv
import os


headers = {
    "accept": "application/json"
}

# OpenAI API variables

model = "gpt-4-1106-preview"
load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)





HEIGHT_ABOVE_GROUND_2 = "https://climathon.iblsoft.com/data/gfs-0.5deg/edr/collections/height-above-ground_2"
HEIGHT_ABOVE_GROUND_2_PARAMS ={
    "maximum-temperature_stat:max/PT3H": "Maximum temperature - Maximum 3h",
    "minimum-temperature_stat:min/PT3H": "Minimum temperature - Minimum 3h"
}
HEIGHT_ABOVE_GROUND_3 = "https://climathon.iblsoft.com/data/gfs-0.5deg/edr/collections/height-above-ground_3"
HEIGHT_ABOVE_GROUND_3_PARAMS = {
    "maximum-temperature_stat:max/PT6H": "Maximum temperature - Maximum 6h",
    "minimum-temperature_stat:min/PT6H": "Minimum temperature - Minimum 6h"
}

# medium range 3h
SINGLE_LAYER_2 = "https://climathon.iblsoft.com/data/gfs-0.5deg/edr/collections/single-layer_2"
SINGLE_LAYER_2_PARAMETERS ={
    "temperature_low-cld-top_stat:avg/PT3H": "Temperature - Low cloud top level - Average 3h",
    "temperature_mid-cld-top_stat:avg/PT3H": "Temperature - Middle cloud top level - Average 3h",
    "temperature_high-cld-top_stat:avg/PT3H": "Temperature - High cloud top level - Average 3h",
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
    "pressure_low-cld-bottom_stat:avg/PT3H": "Pressure - Low cloud bottom level - Average 3h",
    "pressure_low-cld-top_stat:avg/PT3H": "Pressure - Low cloud top level - Average 3h",
    "pressure_mid-cld-bottom_stat:avg/PT3H": "Pressure - Middle cloud bottom level - Average 3h",
    "pressure_mid-cld-top_stat:avg/PT3H": "Pressure - Middle cloud top level - Average 3h",
    "pressure_high-cld-bottom_stat:avg/PT3H": "Pressure - High cloud bottom level - Average 3h",
    "pressure_high-cld-top_stat:avg/PT3H": "Pressure - High cloud top level - Average 3h",
    "zonal-flux-of-gravity-wave-stress_gnd-surf_stat:avg/PT3H": "Zonal flux of gravity wave stress - Ground surface - Average 3h",
    "meridional-flux-of-gravity-wave-stress_gnd-surf_stat:avg/PT3H": "Meridional flux of gravity wave stress - Ground surface - Average 3h",
    "downward-short-wave-radiation-flux_gnd-surf_stat:avg/PT3H": "Downward short-wave radiation flux - Ground surface - Average 3h",
    "upward-short-wave-radiation-flux_gnd-surf_stat:avg/PT3H": "Upward short-wave radiation flux - Ground surface - Average 3h",
    "upward-short-wave-radiation-flux_atmosphere-top_stat:avg/PT3H": "Upward short-wave radiation flux - Atmosphere top - Average 3h",
    "downward-long-wave-radiation-flux_gnd-surf_stat:avg/PT3H": "Downward long-wave radiation flux - Ground surface - Average 3h",
    "upward-long-wave-radiation-flux_gnd-surf_stat:avg/PT3H": "Upward long-wave radiation flux - Ground surface - Average 3h",
    "upward-long-wave-radiation-flux_atmosphere-top_stat:avg/PT3H": "Upward long-wave radiation flux - Atmosphere top - Average 3h",
    "total-cloud-cover_atmosphere_stat:avg/PT3H": "Total cloud cover - Atmosphere - Average 3h",
    "total-cloud-cover_bound-cloud_stat:avg/PT3H": "Total cloud cover - Boundary layer cloud layer - Average 3h",
    "low-cloud-cover_low-cloud_stat:avg/PT3H": "Low cloud cover - Low cloud layer - Average 3h",
    "medium-cloud-cover_mid-cloud_stat:avg/PT3H": "Medium cloud cover - Middle cloud layer - Average 3h",
    "high-cloud-cover_high-cld_stat:avg/PT3H": "High cloud cover - High cloud layer - Average 3h",
    "cloud-work-function_atmosphere_stat:avg/PT3H": "Cloud work function - Atmosphere - Average 3h",
    "albedo_gnd-surf_stat:avg/PT3H": "Albedo - Ground surface - Average 3h",
    "water-runoff_gnd-surf_stat:acc/PT3H": "Water runoff - Ground surface - Accumulation 3h",
    "ground-heat-flux_gnd-surf_stat:avg/PT3H": "Ground heat flux - Ground surface - Average 3h"
}

# long range 6h
SINGLE_LAYER_3 = "https://climathon.iblsoft.com/data/gfs-0.5deg/edr/collections/single-layer_3"

SINGLE_LAYER_3_PARAMETERS={
    "temperature_low-cld-top_stat:avg/PT6H": "Temperature - Low cloud top level - Average 6h",
    "temperature_mid-cld-top_stat:avg/PT6H": "Temperature - Middle cloud top level - Average 6h",
    "temperature_high-cld-top_stat:avg/PT6H": "Temperature - High cloud top level - Average 6h",
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
    "pressure_low-cld-bottom_stat:avg/PT6H": "Pressure - Low cloud bottom level - Average 6h",
    "pressure_low-cld-top_stat:avg/PT6H": "Pressure - Low cloud top level - Average 6h",
    "pressure_mid-cld-bottom_stat:avg/PT6H": "Pressure - Middle cloud bottom level - Average 6h",
    "pressure_mid-cld-top_stat:avg/PT6H": "Pressure - Middle cloud top level - Average 6h",
    "pressure_high-cld-bottom_stat:avg/PT6H": "Pressure - High cloud bottom level - Average 6h",
    "pressure_high-cld-top_stat:avg/PT6H": "Pressure - High cloud top level - Average 6h",
    "zonal-flux-of-gravity-wave-stress_gnd-surf_stat:avg/PT6H": "Zonal flux of gravity wave stress - Ground surface - Average 6h",
    "meridional-flux-of-gravity-wave-stress_gnd-surf_stat:avg/PT6H": "Meridional flux of gravity wave stress - Ground surface - Average 6h",
    "downward-short-wave-radiation-flux_gnd-surf_stat:avg/PT6H": "Downward short-wave radiation flux - Ground surface - Average 6h",
    "upward-short-wave-radiation-flux_gnd-surf_stat:avg/PT6H": "Upward short-wave radiation flux - Ground surface - Average 6h",
    "upward-short-wave-radiation-flux_atmosphere-top_stat:avg/PT6H": "Upward short-wave radiation flux - Atmosphere top - Average 6h",
    "downward-long-wave-radiation-flux_gnd-surf_stat:avg/PT6H": "Downward long-wave radiation flux - Ground surface - Average 6h",
    "upward-long-wave-radiation-flux_gnd-surf_stat:avg/PT6H": "Upward long-wave radiation flux - Ground surface - Average 6h",
    "upward-long-wave-radiation-flux_atmosphere-top_stat:avg/PT6H": "Upward long-wave radiation flux - Atmosphere top - Average 6h",
    "total-cloud-cover_atmosphere_stat:avg/PT6H": "Total cloud cover - Atmosphere - Average 6h",
    "total-cloud-cover_bound-cloud_stat:avg/PT6H": "Total cloud cover - Boundary layer cloud layer - Average 6h",
    "low-cloud-cover_low-cloud_stat:avg/PT6H": "Low cloud cover - Low cloud layer - Average 6h",
    "medium-cloud-cover_mid-cloud_stat:avg/PT6H": "Medium cloud cover - Middle cloud layer - Average 6h",
    "high-cloud-cover_high-cld_stat:avg/PT6H": "High cloud cover - High cloud layer - Average 6h",
    "cloud-work-function_atmosphere_stat:avg/PT6H": "Cloud work function - Atmosphere - Average 6h",
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
    if previous_element == value_list[-1]:
        return previous_element
    raise Exception('Unexpected error')

def get_weather_data(x, y, from_date, to_date, description):
    duration = abs(to_date-from_date)
    url = None
    if duration <= timedelta(hours=3):
        url = SINGLE_LAYER_2
        temp_url = HEIGHT_ABOVE_GROUND_2
        temp_params = HEIGHT_ABOVE_GROUND_2_PARAMS
        parameters = SINGLE_LAYER_2_PARAMETERS
    else:
        url = SINGLE_LAYER_3
        temp_url = HEIGHT_ABOVE_GROUND_3
        temp_params = HEIGHT_ABOVE_GROUND_3_PARAMS
        parameters = SINGLE_LAYER_3_PARAMETERS
    try:
        date_value = get_dates(from_date, url)
    except Exception as e:
        print("Error: Date in the past" + str(e))
        return None

    completion = client.chat.completions.create(
      model=model,
      response_format={ "type": "json_object" },
      messages=[
        {"role": "system", "content": "You are an expert in predicting how good an activity is based on the weather forecast. You receive a question about a planned activity and a list of possible parameters. Decide based on the activity which parameters you require from the list to answer the query as good as possible. Make sure to only answer parameters that appear in the list. You return a json list of parameters that you need to answer the question in this form: {required_parameters: [parameter1, parameter2, ...]}. Pick only the 5 most important ones." },
        {"role": "user", "content": f"{description}"},
        {"role": "system", "content": f"The list of parameters is: {parameters}"}
      ]
    )

    completion_message_content = completion.choices[0].message.content

    extracted_json = json.loads(completion_message_content)

    parameters= extracted_json['required_parameters']
    print(parameters)

    params = {
        'coords': f'POINT({y} {x})',
        'datetime': date_value.strftime('%Y-%m-%dT%H:%M:%SZ'),
    }

    try:
        # Sending a GET request with parameters
        response = requests.get(url + '/position', params=params)
        if response.status_code == 200:
            general_data = map_response(response, parameters)
            params['z'] = 2
            response = requests.get(temp_url + '/position', params=params)
            temp_data = map_response(response, temp_params)
            return {**general_data,**temp_data}
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    

def map_response(response, parameters):
    temp =  response.json()
    gen_info = temp['parameters']
    values = list(map(lambda x: x['ranges'],temp['coverages']))
    values = {list(value.keys())[0]:list(value.values())[0] for value in values}
    return {param: {'unit':gen_info[param]['unit']['symbol'], 'description':gen_info[param]['observedProperty']['label']['en'], 'value': values[param]['values'][0]} for param in parameters if param in values and param in gen_info}