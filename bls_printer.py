import time
import pprint
import bls_functions_and_globals as bls

pp = pprint.PrettyPrinter(indent=4)

time.sleep(1)

seasonal_flag = 'S'

state = 'Hawaii'
start_year = '2004'
end_year = '2013'

seriesid_state = bls.prefix_state + seasonal_flag + bls.bls_area_codes[state] + '03'
seriesid_national = bls.prefix_national + seasonal_flag + bls.bls_area_codes['National']

series_ids = [seriesid_state, seriesid_national]

year_to_state = bls.get_bls_data(series_ids, start_year, end_year, 'Y')

for year in sorted(year_to_state.keys()):
    for month in year_to_state[year]:
        print_me = "{0}, {1}: ".format(month, year)
        for state in year_to_state[year][month]:
                print_me = "{0}{1} ({2})\t".format(print_me, state, year_to_state[year][month][state])
        if month == 'August':
            print(print_me)
