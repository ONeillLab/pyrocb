
import numpy as np
import sys
import os 

utils_path = f"{os.environ['PCB_SCRIPTS_DIR']}/utils"
out_path = os.environ["PCB_OUT_DIR"]

sys.path.append(utils_path)
from configutils import fbp_get_val
def forest_floor_consumption(fuel_category_id, fine_fuel_moisture_code, buildup_index):
    """Computes the forest floor consumption based on Forestry Canada. 1992 eqs. 13, 19, 21, 23"""
    ffc = 0
    if fuel_category_id == 7:
        # Forestry Canada. 1992 eq. 13
        ffc = 2 * (1 - np.exp(-0.104 * (fine_fuel_moisture_code - 70))) 
    elif fuel_category_id == 21:
        # Forestry Canada. 1992 eq. 19 
        ffc = 4 * (1 - np.exp(-0.025 * buildup_index))
    elif fuel_category_id == 22:
        # Forestry Canada. 1992 eq. 21
        ffc = 10 * (1 - np.exp(-0.013 * buildup_index))
    elif fuel_category_id == 23:
        # Forestry Canada. 1992 eq. 23
        ffc = 12 * (1 - np.exp(-0.0166 * buildup_index))

    return max(ffc, 0)

def woody_fuel_consumption(fuel_category_id, fine_fuel_moisture_code, buildup_index):
    """Computes the woody fuel consumption based on Forestry Canada. 1992 eqs. 14, 20, 22, 24"""
    wfc = 0
    if fuel_category_id == 7:
        # Forestry Canada. 1992 eq. 14
        wfc = 1.5 * (1 - np.exp(-0.0201 * buildup_index))
    elif fuel_category_id == 21:
        # Forestry Canada. 1992 eq. 20 
        wfc = 4 * (1 - np.exp(-0.034 * buildup_index))
    elif fuel_category_id == 22:
        # Forestry Canada. 1992 eq. 22
        wfc = 6 * (1 - np.exp(-0.060 * buildup_index))
    elif fuel_category_id == 23:
        # Forestry Canada. 1992 eq. 24
        wfc = 20 * (1 - np.exp(-0.0210 * buildup_index))

    return max(wfc, 0)

def surface_fuel_consumption(fuel_category_id, fine_fuel_moisture_code, buildup_index):
    """Computes the surface fuel based on Forestry Canada. 1992 eqs. 10, 11, 12, 15, 16, 17, 25 and B.M. Wotton. 2009 eqs. 9a, 9b, and section 3.1.2"""
    sfc = 0
    if fuel_category_id == 1:
        # B.M. Wotton. 2009 eqs. 9a, 9b
        sfc = 0.75 * (1 + np.sign(fine_fuel_moisture_code - 84) * (1 - np.exp(-0.23 * abs(fine_fuel_moisture_code - 84))) ** 0.5)
    elif fuel_category_id in (31, 32):
        # B.M. Wotton. 2009 section 3.1.2
        sfc = 0.35
    elif fuel_category_id in (2, 70, 80, 90):
        # Forestry Canada. 1992 eq. 10
        sfc = 5 * (1 - np.exp(-0.0115 * buildup_index))
    elif fuel_category_id in (3, 4):
        # Forestry Canada. 1992 eq. 11
        sfc = 5 * (1 - np.exp(-0.0164 * buildup_index)) ** 2.24
    elif fuel_category_id in (5, 6):
        # Forestry Canada. 1992 eq. 12
        sfc = 5 * (1 - np.exp(-0.0149 * buildup_index)) ** 2.48
    elif fuel_category_id in (11, 13):
        # Forestry Canada. 1992 eq. 16
        sfc = 1.5 * (1 - np.exp(-0.0183 * buildup_index))
    elif 400 < fuel_category_id and fuel_category_id < 700:
        # Forestry Canada. 1992 eq. 17
        percent_conifer = fuel_category_id % 100
        percent_hardwood = 100 - percent_conifer
        sfc = (percent_conifer / 100 * surface_fuel_consumption(2, fine_fuel_moisture_code, buildup_index)) + (percent_hardwood / 100 * surface_fuel_consumption(11, fine_fuel_moisture_code, buildup_index))
    elif fuel_category_id in (7, 21, 22, 23):
        # Forestry Canada. 1992 eqs. 15, 25
        return forest_floor_consumption(fuel_category_id, fine_fuel_moisture_code, buildup_index) + woody_fuel_consumption(fuel_category_id, fine_fuel_moisture_code, buildup_index)

    return max(0, sfc)

if __name__ == "__main__":

    crosswalks = []
    for profile in os.scandir(f"{out_path}/output/crosswalk"):
        if not profile.is_dir():
            continue
        
        label = profile.name
        csvs = os.scandir(profile.path)
        for csv in csvs:
            if not csv.is_file() or not csv.name.endswith('.csv'):
                continue

            crosswalks.append((label, csv.name, csv.path))
    crosswalks.sort()

    for i in range(len(crosswalks)):
        print(f"{i + 1}: {crosswalks[i][0]}, {crosswalks[i][1]}")
    in_str = input(f"Enter a crosswalk selection (this only is used to get a list of FBP fuel types, so pick a crosstab in/near your region of interest) (1 - {len(crosswalks)}):").strip()
    crosswalk_i = int(in_str) - 1
    crosswalk_profile, crosswalk_name, crosswalk_path = crosswalks[crosswalk_i]
    print(f"Using crosswalk: {crosswalk_profile}, {crosswalk_name}")

    ffmc = fbp_get_val("ffmc")
    bui = fbp_get_val("bui")

    print(f"Using Fine Fuel Moisture Code: {ffmc} and Buildup Index: {bui} from fbp.json.")
    with open(crosswalk_path, "r") as crosswalk:
        crosswalk_data = crosswalk.readlines()[1:]
        for line in crosswalk_data:
            cad_id, _, _ = line.strip().split(",")
            cad_id = int(cad_id.strip())
            sfc = surface_fuel_consumption(cad_id, ffmc, bui)
            print(f"{cad_id}: {sfc}")
