import pandas as pd
import openai
openai.api_key = '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'
class car_cut:
    def __init__(self, cut_id, cut_all, dtc_all, retarder_all, switch_all):
        self.cut_id = cut_id
        self.cut = cut_all[cut_all['Cut Record ID'] == cut_id]
        self.dtc = dtc_all
        self.retarder = retarder_all[retarder_all['Cut Record ID'] == cut_id]
        self.switch = switch_all[switch_all['Cut Record ID'] == cut_id]

    def calculate_rollability(self):
        # This function should implement the calculation of rollability based on DTC data.
        # The exact formula or method to calculate this isn't clear from the provided information
        # So, here we'll just define a placeholder
        pass

def load_data():
    dtc_all = pd.read_csv("TUL_09012021_DTC_DATA.CSV")
    cut_all = pd.read_csv("TUL_09012021_CUT_DATA.CSV")
    retarder_all = pd.read_csv("TUL_09012021_RETARDER_DATA.CSV")
    switch_all = pd.read_csv("TUL_09012021_SWITCH_DATA.CSV")

    return dtc_all, cut_all, retarder_all, switch_all

# Load the data
dtc_all, cut_all, retarder_all, switch_all = load_data()

# Merge the parameters of cut_all and retarder_all together every line if they have the same Car Number.
merged_data = pd.merge(cut_all, retarder_all, on="Car Number", suffixes=('_cut', '_retarder'), how="inner")
merged_data = pd.merge(merged_data, switch_all, on="Car Number", how="inner")

# Show one output case
merged_data.to_csv("merged_data.csv", index=False)