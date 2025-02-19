import time

import pandas as pd

from adap.api_automation.utils.data_util import get_data_file, read_data_from_file

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

technical_columns = ["unit id",
                     "state",
                     "judgments",
                     "agreement",
                     "checkbox0",
                     "checkbox1",
                     "index"]


def collect_data_from_ui_table(driver, ignore_technical_columns=True):
    driver.implicitly_wait(0.5)
    next_page = True
    # driver.implicitly_wait(1)
    columns = []

    el_collumns = driver.find_elements('xpath',"//th")
    index = 0
    for c in el_collumns:
        label = c.text
        # label = c.get_attribute('aria-label').split(':')[0]
        if label:
            columns.append(label.lower())
        else:
            columns.append("checkbox"+str(index))
        index +=1


    data = []
    while next_page:
        i = 1
        row_on_page = driver.find_elements('xpath',"//tbody//tr")
        for row in row_on_page:
            row_data_ui = row.find_elements('xpath',".//td")
            row_data = []
            for data_element in row_data_ui:
                data_element_class = data_element.get_attribute('class')
                if data_element_class == ' select-all':
                    continue
                if data_element_class == ' center':
                    _data = data_element.text
                elif 'text-nowrap' in data_element_class:
                    _data = data_element.find_elements('xpath',"./a")[0].text
                else:
                    _data = data_element.find_elements('xpath',".//div[@class='rebrand-job-units-cell-content']")
                    if len(_data) > 0:
                        _data = _data[0].text
                    else:
                        # new ui
                        # ignore checkbox
                        el = data_element.find_elements('xpath',".//input[@type='checkbox']")
                        if len(el) > 0:
                            _data = el[0].is_selected()
                        #  find unit id
                        el = data_element.find_elements('xpath',".//a[@href]")
                        if len(el) > 0:
                           _data = data_element.find_elements('xpath',".//a")[0].text
                        else:
                            try:
                               _data = data_element.text
                            except:
                               _data = ''
                row_data.append(_data)
            data.append(row_data)
            i += 1

        next_page_link = driver.find_elements('xpath',"//a[@class='rebrand-paginate_button next']")
        if len(next_page_link) > 0:
            next_page_link[0].click()
            time.sleep(1)
        else:
            next_page = False

    driver.implicitly_wait(5)

    df = pd.DataFrame(data, columns=columns)
    if ignore_technical_columns:
        new = delete_technical_columns(df)
        return new
    return df


def delete_technical_columns(df):
    for c in df.columns.values:
        if c in technical_columns:
            df.drop(c, axis=1, inplace=True)
    return df


def collect_data_from_file(file_name, ignore_technical_columns=True):
    data = read_data_from_file(file_name)
    df = pd.DataFrame(data)
    if ignore_technical_columns:
        new = delete_technical_columns(df)
        return new
    return df


def dataframe_equals(df1, df2):
    for c in df1.columns.values:
        df1[c] = df1[c].astype(str)
    for c in df2.columns.values:
        df2[c] = df2[c].astype(str)

    return df1.equals(df2)


def convert_list_to_csv(list_to_convert, filename, column_name=None, index_list=None):
    df = pd.DataFrame(list_to_convert, index=index_list, columns=[column_name])
    csv_file = df.to_csv(filename + ".csv", index=False, )
    return csv_file


def dataframe_compare_on_column(df1, df2, column):
    return df1[column].equals(df2[column])


def replace_column_in_csv(file_name, column_name, value, save=True):
    df = collect_data_from_file(file_name)
    assert column_name in df.keys(), "Column %s has not been found" % column_name
    df[column_name] = value
    #update csv file
    if save:
       df.to_csv(file_name, index_label=False, index=False)
    else:
       return df


def create_updated_csv(file_name, column_name, value, new_name, tmpdir):
    df = replace_column_in_csv(file_name, column_name, value, save=False)
    _file = str(tmpdir) + "/" + new_name
    df.to_csv(_file, index_label=False, index=False)
    return _file


def add_data_in_csv(file_name, new_data):
    df = collect_data_from_file(file_name)
    nwe_df = df.append(new_data, ignore_index=True)
    #update csv file
    nwe_df.to_csv(file_name, index=False, )


def delete_data_from_csv_by_condition(file_name, column, value):
    df = collect_data_from_file(file_name)
    # Get names of indexes for which column Age has value 30
    index = df[df[column] == value].index
    # Delete these row indexes from dataFrame
    df.drop(index, inplace=True)
    #update csv file
    df.to_csv(file_name, index_label=False, )


def copy_file_csv(source_file, tmpdir, file_name):
    df = collect_data_from_file(source_file)
    _file = str(tmpdir) + "/" + file_name

    df.to_csv(_file, index_label=False, )
    return _file

def copy_file_excel(source_file, tmpdir, file_name):
    df = collect_data_from_file(source_file)
    _file = str(tmpdir) + "/" + file_name

    df.to_excel(_file, index_label=False, )
    return _file
