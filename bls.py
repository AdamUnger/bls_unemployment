import bls_functions_and_globals as bls
import cherrypy
import time

# Get these next two from https://github.com/shannonturner/html-table-to-excel
import export_to_xlsx
import html_table_to_excel


class Root(object):

    @cherrypy.expose
    def index(self, **kwargs):

        seasonal = kwargs.get('seasonal')
        measure_code = kwargs.get('measure_code')
        report_state_list = kwargs.get('series[]')
        start_year = kwargs.get('start_year')
        end_year = kwargs.get('end_year')

        page_source = []

        with open('basehtml.txt') as basehtml_file:
            basehtml = basehtml_file.read()
            page_source.append(basehtml)

        if None in (seasonal, measure_code, report_state_list, start_year, end_year):
            return page_source

        else:

            # Prevent passing bad values that aren't options in the form in through POST
            # Very important since we're creating files based off of these.

            if seasonal not in ('S', 'U'):
                return page_source

            if measure_code not in bls.bls_measure_codes.keys():
                return page_source

            if type(report_state_list) == list:
                for state in report_state_list:
                    if state not in bls.state_abbrevs_to_states.keys():
                        return page_source
            elif type(report_state_list) == unicode: # This is needed for when only one state is selected
                report_state_list = [report_state_list]
                for state in report_state_list:
                    if state not in bls.state_abbrevs_to_states.keys():
                        return page_source

            try:
                start_year = int(float(start_year))
            except ValueError:
                return page_source

            try:
                end_year = int(float(end_year))
            except ValueError:
                return page_source

            if start_year > end_year or (end_year - start_year) > 10: # This will also provide validation for the years, though it can't prevent someone from putting an absurd year like 1024
                return page_source

            # Sanitation finished; it is now safe to create filenames based off of these values.

            table_title = []

            table_title.append('Seasonally Adjusted') if seasonal == 'S' else table_title.append('Not Seasonally Adjusted')

            if measure_code == '03':
                table_title.append('Unemployment Rate')
            elif measure_code == '04':
                table_title.append('Unemployment Numbers')
            elif measure_code == '05':
                table_title.append('Employment Numbers')
            elif measure_code == '06':
                table_title.append('Labor Force Numbers')

            table_title.append(' for: {0}'.format(', '.join(report_state_list)))
            table_title.append('({0} - {1})'.format(start_year, end_year))

            page_source.append('<br><h2 style="text-align: center;">{0}</h2><br>'.format(' '.join(table_title)))

            bls_data = get_blsdata(seasonal, start_year, end_year, measure_code, report_state_list)

            if (bls_data == 'No results returned' or bls_data == 'Only 10 years may be viewed at a time.'):
                page_source.append(bls_data)
                return page_source

            generated_filename = 'exports/export_{0}{1}{2}{3}{4}.xlsx'.format(seasonal, measure_code, ''.join(report_state_list), start_year, end_year)
            export_to_xlsx.export_to_xlsx(html_table_to_excel.html_table_to_excel(bls_data), filename=generated_filename, reverse=True)
            page_source.append('<br><center><b><a href="{0}" target="_blank">Download to Excel</a></b></center><br>'.format(generated_filename))

            page_source.append('<br><center>{0}</center>'.format(bls_data))

            return page_source

def get_blsdata(seasonal_flag, start_year, end_year, measure_code, series):

    """ get_blsdata(seasonal_flag, start_year, end_year, measure_code, series): This function is adapted from the command-line version I contributed to at https://github.com/AdamUnger/bls_unemployment/blob/master/bls_printer.py
    """

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
        return "No results returned."

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

    build_html_table.append('</table>')

    return '\n'.join(build_html_table)


if __name__ == '__main__':

    cherrypy.quickstart(Root(), '/', 'cfg.cfg')
