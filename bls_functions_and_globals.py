import requests
import json

# Global Variables

bls_measure_codes = {
    '03':   'unemployment rate',
    '04':   'unemployment',
    '05':   'employment',
    '06':   'labor force'
    }

bls_area_codes = {
    'Alabama': 'ST010000',
    'Alaska': 'ST020000',
    'Arizona': 'ST040000',
    'Arkansas': 'ST050000',
    'California': 'ST060000',
    'Colorado': 'ST080000',
    'Connecticut': 'ST090000',
    'Delaware': 'ST100000',
    'District of Columbia': 'ST110000',
    'Florida': 'ST120000',
    'Georgia': 'ST130000',
    'Hawaii': 'ST150000',
    'Idaho': 'ST160000',
    'Illinois': 'ST170000',
    'Indiana': 'ST180000',
    'Iowa': 'ST190000',
    'Kansas': 'ST200000',
    'Kentucky': 'ST210000',
    'Louisiana': 'ST220000',
    'Maine': 'ST230000',
    'Maryland': 'ST240000',
    'Massachusetts': 'ST250000',
    'Michigan': 'ST260000',
    'Minnesota': 'ST270000',
    'Mississippi': 'ST280000',
    'Missouri': 'ST290000',
    'Montana': 'ST300000',
    'Nebraska': 'ST310000',
    'Nevada': 'ST320000',
    'New Hampshire': 'ST330000',
    'New Jersey': 'ST340000',
    'New Mexico': 'ST350000',
    'New York': 'ST360000',
    'North Carolina': 'ST370000',
    'North Dakota': 'ST380000',
    'Ohio': 'ST390000',
    'Oklahoma': 'ST400000',
    'Oregon': 'ST410000',
    'Pennsylvania': 'ST420000',
    'Puerto Rico': 'ST430000',
    'Rhode Island': 'ST440000',
    'South Carolina': 'ST450000',
    'South Dakota': 'ST460000',
    'Tennessee': 'ST470000',
    'Texas': 'ST480000',
    'Utah': 'ST490000',
    'Vermont': 'ST500000',
    'Virginia': 'ST510000',
    'Washington': 'ST530000',
    'West Virginia': 'ST540000',
    'Wisconsin': 'ST550000',
    'Wyoming': 'ST560000',
    'National': '14000000'
    }

bls_series_id_to_state = {}

for state in bls_area_codes:
   bls_series_id_to_state.update({bls_area_codes[state]:state})

month_to_number = {
   'January': '01',
   'February': '02',
   'March': '03',
   'April': '04',
   'May': '05',
   'June': '06',
   'July': '07',
   'August': '08',
   'September': '09',
   'October': '10',
   'November': '11',
   'December': '12'
   }

number_to_month = {}

for month in month_to_number:
   number_to_month.update({month_to_number[month]: month})

state_abbrevs_to_states = {
   'ZZ': 'National',
   'AL': 'Alabama',
   'AK': 'Alaska',
   'AZ': 'Arizona',
   'AR': 'Arkansas',
   'CA': 'California',
   'CO': 'Colorado',
   'CT': 'Connecticut',
   'DE': 'Delaware',
   'DC': 'District Of Columbia',
   'FL': 'Florida',
   'GA': 'Georgia',
   'HI': 'Hawaii',
   'ID': 'Idaho',
   'IL': 'Illinois',
   'IN': 'Indiana',
   'IA': 'Iowa',
   'KS': 'Kansas',
   'KY': 'Kentucky',
   'LA': 'Louisiana',
   'ME': 'Maine',
   'MD': 'Maryland',
   'MA': 'Massachusetts',
   'MI': 'Michigan',
   'MN': 'Minnesota',
   'MS': 'Mississippi',
   'MO': 'Missouri',
   'MT': 'Montana',
   'NE': 'Nebraska',
   'NV': 'Nevada',
   'NH': 'New Hampshire',
   'NJ': 'New Jersey',
   'NM': 'New Mexico',
   'NY': 'New York',
   'NC': 'North Carolina',
   'ND': 'North Dakota',
   'OH': 'Ohio',
   'OK': 'Oklahoma',
   'OR': 'Oregon',
   'PA': 'Pennsylvania',
   'RI': 'Rhode Island',
   'SC': 'South Carolina',
   'SD': 'South Dakota',
   'TN': 'Tennessee',
   'TX': 'Texas',
   'UT': 'Utah',
   'VT': 'Vermont',
   'VA': 'Virginia',
   'WA': 'Washington',
   'WV': 'West Virginia',
   'WI': 'Wisconsin',
   'WY': 'Wyoming'
      }

bls_url = 'http://api.bls.gov/publicAPI/v1/timeseries/data/'

prefix_state = 'LA'
prefix_national = 'LN'

def get_bls_data (series_ids, start_year, end_year, result_format_flag = 'S'):
    
    payload = {
        "seriesid":series_ids,
        "startyear":start_year, 
        "endyear":end_year
        }

    headers = {'content-type': 'application/json'}

    bls_request_data = requests.post(bls_url, data=json.dumps(payload), headers=headers)
    bls_request_data = bls_request_data.json()
    bls_results = json.loads(bls_request_data['Results'])

    result_set = {}

    for result in bls_results['series']:
        series_id = result['seriesID']
        if series_id == 'LNS14000000':
            area_code = series_id[3:]
        else:
            area_code = series_id[3:-2]
        
        temp_series = {}
        for month_result in result['data']:
            temp_series.update({month_result['year']:{}})

        for month_result in result['data']:
            for year in temp_series.keys():
                if year == month_result['year']:
                    temp_series[year].update({month_result['periodName']:''})

        for month_result in result['data']:
            for year in temp_series.keys():
                if year == month_result['year']:
                    for month in temp_series[year].keys():
                        if month == month_result['periodName']:
                            temp_series[year].update({month:month_result['value']})

        result_set.update({bls_series_id_to_state[area_code]:temp_series})

    if result_format_flag == 'S':
        return (result_set)
    
    elif result_format_flag == 'Y':
        year_to_state = {}

        for state in result_set:
            for year in result_set[state]:
                year_to_state.update({year:{}})
                
        for state in result_set:
            for year in result_set[state]:
                for month in result_set[state][year]:
                    year_to_state[year].update({month:{}})

        for state in result_set:
            for year in result_set[state]:
                for month in result_set[state][year]:
                    year_to_state[year][month].update({state:result_set[state][year][month]})

        return (year_to_state)
    
    else:
        return ("Invalid result_format_flag")
