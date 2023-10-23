import pandas as pd

# Define the dtype of several columns
column_dypes_retarder = {
    'AAR_POOL_ID': str, 
    'KEY_TRN_CD': str,
    'WHL_SCRB_CD': str,
    'PLN_DNGR_CD': str,
    'EXIT_WDETR_FAIL_NME': str
}

column_dtype_switch = {
    'AAR_POOL_ID': str, 
    'KEY_TRN_CD': str,
    'DOT_113_RUL_CD': str,
    'WHL_SCRB_CD': str,
    'PLN_DNGR_CD': str
}
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

def retarder_enter_kinetic_energy(car_cut):
    enter_speed = car_cut.retarder['CUT_FRNT_VEL_QTY'] # fps
    exit_speed = car_cut.retarder['ACTL_EXIT_SPD_RT'] #fps
# Example usage:
car_cut_example = get_car_cut_by_id(car_cuts, "1518942")
print(car_cut_example.retarder)