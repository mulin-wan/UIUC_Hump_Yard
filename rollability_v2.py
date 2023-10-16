import pandas as pd

def import_data(cut_data_file, dtc_data_file, retarder_data_file, switch_data_file):
    cut_data = pd.read_csv(cut_data_file)
    dtc_data = pd.read_csv(dtc_data_file)
    retarder_data = pd.read_csv(retarder_data_file)
    switch_data = pd.read_csv(switch_data_file)

    return cut_data, dtc_data, retarder_data, switch_data
