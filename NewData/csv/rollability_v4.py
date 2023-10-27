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

        enter_kinetic_energy = round(enter_kinetic_energy, 4)
        exit_kinetic_energy = round(exit_kinetic_energy, 4)

        kinetic_energies.append({
            'device_name': device_name,
            'enter_kinetic_energy': enter_kinetic_energy,
            'exit_kinetic_energy': exit_kinetic_energy
        })

    return kinetic_energies

def get_elevations(device_name):
    if pd.isna(device_name):
        return []
    # Filter for rows in the route dataframe that start with the device name
    filtered_data = route[route['Device'].str.startswith(device_name)]
    
    # Extract rows with non-null latitude and elevation
    valid_rows = filtered_data.dropna(subset=['Latitude', 'Elevation'])
    
    if not valid_rows.empty:
        min_lat_row = valid_rows[valid_rows['Latitude'] == valid_rows['Latitude'].min()]
        max_lat_row = valid_rows[valid_rows['Latitude'] == valid_rows['Latitude'].max()]
        
        return [min_lat_row['Elevation'].values[0], max_lat_row['Elevation'].values[0]]
    else:
        return []

def retarder_potential_energy(car_cut):
    mass = int(car_cut.cut['GRS_TONS'].fillna(0).values[0])
    potential_energies = []

    # Iterate through each row in car_cut.retarder
    for index, row in car_cut.retarder.iterrows():
        retarder_name = row['DVC_NME']
        
        # Get elevation data for entering and exiting points
        elevations = get_elevations(retarder_name)

        if elevations:  # Ensure we have both entry and exit elevations
            entering_elevation = elevations[0]
            exiting_elevation = elevations[-1]

            entering_potential_energy = mass * 9.81 * entering_elevation
            exiting_potential_energy = mass * 9.81 * exiting_elevation

            entering_potential_energy = round(entering_potential_energy, 4)
            exiting_potential_energy = round(exiting_potential_energy, 4)

            potential_energies.append({
                'device_name': retarder_name,
                'enter_potential_energy': entering_potential_energy,
                'exit_potential_energy': exiting_potential_energy
            })
        else:
            # If either elevation is missing, append an error message for this specific retarder
            potential_energies.append({
                'device_name': retarder_name,
                'error': f"Elevation value for {retarder_name} is missing or incomplete!"
            })

    return potential_energies

def switch_potential_energy(car_cut):
    mass = int(car_cut.cut['GRS_TONS'].fillna(0).values[0])
    potential_energies = []

    # Iterate through each row in car_cut.switch
    for index, row in car_cut.switch.iterrows():
        switch_name = row['DVC_NME']
        
        # Get elevation data for entering and exiting points
        elevations = get_elevations(switch_name)
        
        if elevations:  # Ensure we have both entry and exit elevations
            entering_elevation = elevations[0]
            exiting_elevation = elevations[1]

            entering_potential_energy = mass * 9.81 * entering_elevation
            exiting_potential_energy = mass * 9.81 * exiting_elevation
            
            entering_potential_energy = round(entering_potential_energy, 4)
            exiting_potential_energy = round(exiting_potential_energy, 4)

            potential_energies.append({
                'device_name': switch_name,
                'enter_potential_energy': entering_potential_energy,
                'exit_potential_energy': exiting_potential_energy
            })
        else:
            # If either elevation is missing, append an error message for this specific switch
            potential_energies.append({
                'device_name': switch_name,
                'error': f"Elevation value for {switch_name} is missing or incomplete!"
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

        front_kinetic_energy = round(front_kinetic_energy, 4)
        rear_kinetic_energy = round(rear_kinetic_energy, 4)

        kinetic_energies.append({
            'device_name': device_name,
            'front_kinetic_energy': front_kinetic_energy,
            'rear_kinetic_energy': rear_kinetic_energy
        })

    return kinetic_energies

results = []

for car_cut in car_cuts:
    # Calculate potential and kinetic energy for each car_cut
    potential_energy_retarder = retarder_potential_energy(car_cut)
    kinetic_energy_retarder = retarder_kinetic_energy(car_cut)
    potential_energy_switch = switch_potential_energy(car_cut)
    kinetic_energy_switch = switch_kinetic_energy(car_cut)

    for data in potential_energy_retarder:
        if pd.notna(data['device_name']):
            # For the retarder's entering potential energy
            results.append({
                'cut_id': car_cut.cut_id,
                'device_name': data['device_name'],
                'energy_type': 'retarder_enter_potential_energy',
                'energy_value': data['enter_potential_energy']
            })
            
            # For the retarder's exiting potential energy
            results.append({
                'cut_id': car_cut.cut_id,
                'device_name': data['device_name'],
                'energy_type': 'retarder_exit_potential_energy',
                'energy_value': data['exit_potential_energy']
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
            # For the switch's entering potential energy
            results.append({
                'cut_id': car_cut.cut_id,
                'device_name': data['device_name'],
                'energy_type': 'switch_enter_potential_energy',
                'energy_value': data['enter_potential_energy']
            })
            
            # For the switch's exiting potential energy
            results.append({
                'cut_id': car_cut.cut_id,
                'device_name': data['device_name'],
                'energy_type': 'switch_exit_potential_energy',
                'energy_value': data['exit_potential_energy']
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
df.to_csv('TULSA-2023-02-20-Month-Energy-v2.csv', index=False)