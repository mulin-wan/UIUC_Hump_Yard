import pandas as pd

# Load CSV Files of 2023-02-20
cut = pd.read_csv('TULSA-2023-02-20-Month-Cut.csv', dtype = str)
retarder = pd.read_csv('TULSA-2023-02-20-Month-Retarder.csv', dtype = str)
switch = pd.read_csv('TULSA-2023-02-20-Month-Switch.csv', dtype = str)
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
    mass = int(car_cut.cut['GRS_TONS'].fillna(0).values[0]) # gross tons
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

    return kinetic_energies

def retarder_potential_energy(car_cut):
    mass = int(car_cut.cut['GRS_TONS'].fillna(0).values[0])
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

def switch_kinetic_energy(car_cut):
    mass = int(car_cut.cut['GRS_TONS'].fillna(0).values[0]) # gross tons
    kinetic_energies = []
    # Iterate through each row in car_cut.switch
    for index, row in car_cut.switch.iterrows():
        front_speed = float(row['CUT_FRNT_VEL_QTY'])  # fps
        rear_speed = float(row['REAR_VEL_QTY'])   # fps
        device_name = row['DVC_NME']

        front_kinetic_energy = 0.5 * mass * front_speed ** 2
        rear_kinetic_energy  = 0.5 * mass * rear_speed ** 2

        kinetic_energies.append({
            'device_name': device_name,
            'front_kinetic_energy': front_kinetic_energy,
            'rear_kinetic_energy': rear_kinetic_energy
        })

    return kinetic_energies

def switch_potential_energy(car_cut):
    mass = int(car_cut.cut['GRS_TONS'].fillna(0).values[0])
    potential_energies = []

    # Iterate through each row in car_cut.switch
    for index, row in car_cut.switch.iterrows():
        device_name = row['DVC_NME']

        # Filter the route DataFrame for rows containing {device_name}SWD and have non-null Elevation
        find_switch_elevation = route[(route['Device'] == f"{device_name}SWD") & (route['Elevation'].notnull())]

        # If there are multiple rows with non-null Elevation, take the first one for each
        switch_elevation = find_switch_elevation['Elevation'].iloc[0] if not find_switch_elevation.empty else None

        # Check if both elevations are available
        if switch_elevation is not None:
            # If both elevations are the same or different, calculate the average
            potential_energy = mass * 9.81 * float(switch_elevation)  # Assuming g = 9.81 m/s^2 for potential energy calculation
            
            potential_energies.append({
                'device_name': device_name,
                'potential_energy': potential_energy
            })

        else:
            # If either elevation is missing, append an error message for this specific retarder
            potential_energies.append({
                'device_name': device_name,
                'error': f"Elevation values for {device_name}SWD is missing!"
            })

    return potential_energies

results = []

for car_cut in car_cuts:
    # Calculate potential and kinetic energy for each car_cut
    potential_energy_retarder = retarder_potential_energy(car_cut)
    kinetic_energy_retarder = retarder_kinetic_energy(car_cut)
    potential_energy_switch = switch_potential_energy(car_cut)
    kinetic_energy_switch = switch_kinetic_energy(car_cut)

    for data in potential_energy_retarder:
        if pd.notna(data['device_name']):
            #print("car_cut", car_cut.cut_id, "data value:", data)
            results.append({
                'cut_id': car_cut.cut_id,
                'device_name': data['device_name'],
                'energy_type': 'retarder_potential_energy',
                'energy_value': data['potential_energy']
            })

    for data in kinetic_energy_retarder:
        if pd.notna(data['device_name']):
            results.append({
                'cut_id': car_cut.cut_id,
                'device_name': data['device_name'],
                'energy_type': 'retarder_enter_kinetic_energy',
                'energy_value': data['enter_kinetic_energy']
            })
            results.append({
                'cut_id': car_cut.cut_id,
                'device_name': data['device_name'],
                'energy_type': 'retarder_exit_kinetic_energy',
                'energy_value': data['exit_kinetic_energy']
            })

    for data in potential_energy_switch:
        if pd.notna(data['device_name']):
            results.append({
                'cut_id': car_cut.cut_id,
                'device_name': data['device_name'],
                'energy_type': 'switch_potential_energy',
                'energy_value': data['potential_energy']
            })

    for data in kinetic_energy_switch:
        if pd.notna(data['device_name']):
            results.append({
                'cut_id': car_cut.cut_id,
                'device_name': data['device_name'],
                'energy_type': 'switch_front_kinetic_energy',
                'energy_value': data['front_kinetic_energy']
            })
            results.append({
                'cut_id': car_cut.cut_id,
                'device_name': data['device_name'],
                'energy_type': 'switch_rear_kinetic_energy',
                'energy_value': data['rear_kinetic_energy']
            })

# Convert the results list to a DataFrame and save it to a CSV
df = pd.DataFrame(results)
df.to_csv('TULSA-2023-02-20-Month-Energy.csv', index=False)