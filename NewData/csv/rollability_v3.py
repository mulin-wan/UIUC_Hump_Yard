import pandas as pd
import numpy as np

# Load CSV Files of 2023-02-20
cut = pd.read_csv('TULSA-2023-02-20-Month-Cut-Test.csv', dtype = str)
retarder = pd.read_csv('TULSA-2023-02-20-Month-Retarder-Test.csv', dtype = str)
switch = pd.read_csv('TULSA-2023-02-20-Month-Switch-Test.csv', dtype = str)
route = pd.read_csv('Route Sheet Tulsa.csv')

class CarCut:
    def __init__(self, cut_id):
        self.cut_id = cut_id
        self.cut = None
        self.retarder = None
        self.switch = None
    
    def populate(self, cut, retarder, switch):
        # Assuming you want to match against the shortened Cut Record ID
        short_id = cut['HMP_CUT_ID'].astype(str).str[:-1]
        
        self.cut = cut[short_id == self.cut_id]
        self.retarder = retarder[retarder['HMP_CUT_ID'].astype(str).str[:-1] == self.cut_id]
        self.switch = switch[switch['HMP_CUT_ID'].astype(str).str[:-1] == self.cut_id]

car_cuts = []
# Convert 'HMP_CUT_ID' to string, slice to remove last character, and then get unique values
cut_id_list = cut['HMP_CUT_ID'].astype(str).str[:-1].unique() # An array of all cut record ID without last digit

for cut_id in cut_id_list:
    car_cut_obj = CarCut(cut_id)
    car_cut_obj.populate(cut, retarder, switch)
    car_cuts.append(car_cut_obj)

def get_car_cut_by_id(car_cuts, target_cut_id):
    for car_cut in car_cuts:
        if car_cut.cut_id == target_cut_id:
            return car_cut
    return None

def retarder_kinetic_energy(car_cut):
    mass = int(car_cut.cut['GRS_TONS'].values[0]) # gross tons
    kinetic_energies = []
    # Iterate through each row in car_cut.retarder
    for index, row in car_cut.retarder.iterrows():
        enter_speed = float(row['CUT_FRNT_VEL_QTY'])  # fps
        exit_speed = float(row['ACTL_EXIT_SPD_RT'])   # fps
        device_name = row['DVC_NME']

        enter_kinetic_energy = 0.5 * mass * enter_speed ** 2
        exit_kinetic_energy  = 0.5 * mass * exit_speed ** 2

        kinetic_energies.append({
            'device_name': device_name,
            'enter_kinetic_energy': enter_kinetic_energy,
            'exit_kinetic_energy': exit_kinetic_energy
        })
    print(kinetic_energies)
    return kinetic_energies

def retarder_potential_energy(car_cut):
    mass = int(car_cut.cut['GRS_TONS'].values[0]) 
    potential_energies = []

    # Iterate through each row in car_cut.retarder
    for index, row in car_cut.retarder.iterrows():
        retarder_name = row['DVC_NME']

        # Filter the route DataFrame for rows containing {retarder_name}NWDL or {retarder_name}NWDR and have non-null Elevation
        nwdl_route_data = route[(route['Device'] == f"{retarder_name}NWDL") & (route['Elevation'].notnull())]
        nwdr_route_data = route[(route['Device'] == f"{retarder_name}NWDR") & (route['Elevation'].notnull())]

        # If there are multiple rows with non-null Elevation, take the first one for each
        nwdl_elevation = nwdl_route_data['Elevation'].iloc[0] if not nwdl_route_data.empty else None
        nwdr_elevation = nwdr_route_data['Elevation'].iloc[0] if not nwdr_route_data.empty else None

        # Check if both elevations are available
        if nwdl_elevation is not None and nwdr_elevation is not None:
            # If both elevations are the same or different, calculate the average
            elevation = (float(nwdl_elevation) + float(nwdr_elevation)) / 2
            potential_energy = mass * 9.81 * elevation  # Assuming g = 9.81 m/s^2 for potential energy calculation
            
            potential_energies.append({
                'device_name': retarder_name,
                'potential_energy': potential_energy
            })

        else:
            # If either elevation is missing, append an error message for this specific retarder
            potential_energies.append({
                'device_name': retarder_name,
                'error': f"Elevation values for {retarder_name}NWDL or {retarder_name}NWDR are missing!"
            })

    return potential_energies

# Example usage:
car_cut_example = get_car_cut_by_id(car_cuts, "1518942")
# print(retarder_kinetic_energy(car_cut_example))
print(retarder_potential_energy(car_cut_example))