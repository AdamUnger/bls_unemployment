import bls_functions_and_globals as bls
import sys
import time

if __name__ == '__main__':

    try:
        
        seasonal_flag = sys.argv[1]
        start_year = int(sys.argv[2])
        end_year = int(sys.argv[3])
        measure_code = sys.argv[4]
        series = sys.argv[5:]

    except IndexError:

        print """Arguments for bls_printer.py: seasonal_flag, start_year, end_year, measure_code, series_states (abbreviations, separate by spaces.  Use ZZ for national.)
    Example: python bls_printer.py S 2004 2013 03 AZ CO NM ZZ
        """
        sys.exit(1)

    if start_year > end_year or (end_year - start_year) > 10:

        print "Only 10 ten years may be viewed at a time."
        sys.exit(1)        

    months = sorted(bls.month_to_number.values())
    years = sorted(range(start_year, end_year + 1))

    months.reverse()
    years.reverse()

    states = []
    series_ids = []
    for state in series:
        try:
            if bls.state_abbrevs_to_states[state] == 'National':
                series_ids.append('{0}{1}{2}'.format(bls.prefix_national, seasonal_flag, bls.bls_area_codes[bls.state_abbrevs_to_states[state]]))
            else:
                series_ids.append('{0}{1}{2}{3}'.format(bls.prefix_state, seasonal_flag, bls.bls_area_codes[bls.state_abbrevs_to_states[state]], measure_code))
            states.append(bls.state_abbrevs_to_states[state])
        except KeyError:
            continue # If an invalid state is entered

    bls_data = bls.get_bls_data(series_ids, start_year, end_year, 'S')

    if len(bls_data) == 0:
        print "No results returned."
        sys.exit(1)

    if 'National' in states:
        states.remove('National')
        states.append('National') # If National exists, move it to the end

    # BUILD HTML TABLE FOR RETURNS
    
    build_html_table = []

    build_html_table.append('<table cellpadding=2 style="vertical-align: middle; text-align: center;"><tr>')
    build_html_table.append('<td></td>') # Empty corner cell at 0,0

    # Header row with states
    for state in states:
        build_html_table.append('<td>{0}</td>'.format(state))

    build_html_table.append('</tr>')

    (current_year, current_month) = time.localtime()[0:2]
    if current_month < 10:
        current_month = str('0{0}'.format(current_month))

    for year in years:
        for month in months:
            if (year < current_year) or (year == current_year and month < current_month):
                build_html_table.append('<tr><td>{0} {1}</td>'.format(bls.number_to_month[month], year))
                for state in states:
                    try:
                        build_html_table.append('<td>{0}</td>'.format(bls_data[state][str(year)][bls.number_to_month[month]]))
                    except KeyError:
                        build_html_table.append('<td>---</td>')
                build_html_table.append('</tr>')
        build_html_table.append('</tr>')

    build_html_table.append('</table>')

    print '\n'.join(build_html_table)
