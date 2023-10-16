import pandas as pd

class car_cut:
    def __init__(self, cut_data_row, dtc_data, retarder_data, start_from_index=None):
        self.cut_data = cut_data_row
        self.car_weight = cut_data_row['Cut Gross Tons']
        self.num_cars = cut_data_row['#Cars in Cut']
        dtc_data['TimeStamp'] = pd.to_datetime(dtc_data['TimeStamp'])
        dtc_data_group = dtc_data[dtc_data['Track'] == cut_data_row['Desination Track']]
        retarder_row = retarder_data[(retarder_data['Car Number'] == cut_data_row['Car Number']) & (retarder_data['Retarder Name'].str.startswith('RTG'))].iloc[0]
        self.entering_speed = retarder_row['Entering Speed Actual (fps)']
        self.entering_timestamp = retarder_row['Entering TimeStamp Actual']
        self.crest_time = retarder_row['Crest Time']

        # Get the running time before entering the retarder
        self.running_time_before_entering = (self.entering_timestamp - self.crest_time).total_seconds()

        if start_from_index is None:
            start_index = dtc_data_group[dtc_data_group['TimeStamp'] >= cut_data_row['Crest Time']].index[0]
        else:
            if len(dtc_data_group[dtc_data_group.index > start_from_index]) > 0:
                start_index = dtc_data_group[dtc_data_group.index > start_from_index].index[0]
            else:
                self.end_index = None
                return
        try:
            end_index = dtc_data_group[(dtc_data_group['DTC Footage'] < 10) & (dtc_data_group['DTC Footage'].diff() < -50) & (dtc_data_group.index > start_index)].index[0]
        except IndexError:
            end_index = dtc_data_group.index[-1]

        self.dtc_data = dtc_data_group.loc[start_index:end_index]
        self.end_index = end_index

    def calculate_acceleration(self):
        acceleration = self.entering_speed / self.running_time_before_entering
        #print(f"Car Number: {self.cut_data['Car Number']}, Acceleration: {acceleration}")
        return acceleration

    def calculate_rollability(self):
        acceleration = self.calculate_acceleration()
        resistance = self.car_weight * acceleration * 2000  # Convert tons to lbs
        #print(f"Car Number: {self.cut_data['Car Number']}, Resistance: {resistance}")
        rollability = resistance / (self.car_weight * self.num_cars)
        #rollability = resistance / self.car_weight
        #print(f"Car Number: {self.cut_data['Car Number']}, Rollability: {rollability}")
        return rollability

def import_data(cut_data_file, dtc_data_file, retarder_data_file):
    cut_data = pd.read_csv(cut_data_file)
    dtc_data = pd.read_csv(dtc_data_file)
    retarder_data = pd.read_csv(retarder_data_file)
    
    # Convert the time columns to datetime objects
    cut_data['Crest Time'] = pd.to_datetime(cut_data['Crest Time'])
    retarder_data['Crest Time'] = pd.to_datetime(retarder_data['Crest Time'])  # Ensure this column is also converted to datetime
    retarder_data['Entering TimeStamp Actual'] = pd.to_datetime(retarder_data['Entering TimeStamp Actual'])
    
    # Continue with your existing logic to create car cuts
    car_cuts = []
    for track, group in cut_data.groupby('Desination Track'):
        group = group.sort_values(by='Crest Time')
        last_end_index = None
        for i in range(len(group)):
            car_cut = car_cut(group.iloc[i], dtc_data, retarder_data, last_end_index)
            if car_cut.end_index is not None:
                car_cuts.append(car_cut)
                last_end_index = car_cut.end_index
    return car_cuts

def export_rollability(car_cuts, output_file):
    if 'Car Number' not in car_cuts[0].cut_data:
        print("Car Number column missing. Available columns:", car_cuts[0].cut_data.keys())
        return
    rollability_data = [{"Car Number": cut.cut_data['Car Number'], "Rollability (lbs)": cut.calculate_rollability()} for cut in car_cuts]
    rollability_df = pd.DataFrame(rollability_data)
    rollability_df.to_csv(output_file, index=False)

car_cuts = import_data('TUL_09012021_CUT_DATA.CSV', 'TUL_09012021_DTC_DATA.CSV', 'TUL_09012021_RETARDER_DATA.CSV')
export_rollability(car_cuts, 'TUL_09012021_ROLLABILITY_DATA.csv')