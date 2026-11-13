
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
        sfc = forest_floor_consumption(fuel_category_id, fine_fuel_moisture_code, buildup_index) + woody_fuel_consumption(fuel_category_id, fine_fuel_moisture_code, buildup_index)

    return max(0, sfc)

# Rate of Spread computations
def fine_fuel_moisture_content(fine_fuel_moisture_code):
    """Computes the Fine fuel moisture content in percent based on Forestry Canada. 1992 eq. 46"""
    m = (147.2 * (101 - fine_fuel_moisture_code)) / (59.5 + fine_fuel_moisture_code)
    return m

def fine_fuel_moisture_function(fine_fuel_moisture_code):
    """Computes the Fine fuel moisture function in the initial spread index based on Forestry Canada. 1992 eq. 45"""
    m = fine_fuel_moisture_content(fine_fuel_moisture_code)
    f_of_f = 91.9 * np.exp(-0.1386 * m) * (1 + (m ** 5.31) / 4.93e7)
    return f_of_f

def initial_spread_index_no_slope(fine_fuel_moisture_code):
    """Computes the final initial spread index with no wind or slope adjustment based on Forestry Canada. 1992 eq. 52"""
    f_of_f = fine_fuel_moisture_function(fine_fuel_moisture_code)
    f_of_w = 1 # No adjustment due to wind, Forestry Canada eq. 53
    isi = 0.208 * f_of_w * f_of_f
    return isi


def a_coefficient(fuel_category_id):
    """Computes the rate of spread equation coefficient a based on Forestry Canada. 1992 Table 6, eqs. 29, 32"""
    a = 0
    if fuel_category_id == 1:
        # C-1
        a = 90
    elif fuel_category_id in (2, 3, 4):
        # C-2, C-3, C-4
        a = 110
    elif fuel_category_id in (5, 6, 11, 13):
        # C-5, C-6, D-1, D-1/2
        a = 30
    elif fuel_category_id == 12:
        # D-2
        raise Exception("No equation implemented for D-2 fuel type as it was not introduces in the Forestry Canada. 1992 report")
    elif fuel_category_id == 7:
        # C-7
        a = 45
    elif fuel_category_id == 21:
        # S-1
        a = 75
    elif fuel_category_id == 22:
        # S-2
        a = 40
    elif fuel_category_id == 23:
        # S-3
        a = 55
    elif fuel_category_id == 31:
        # O-1a
        a = 190
    elif fuel_category_id == 32:
        # O-1b
        a = 250
    elif 700 < fuel_category_id and fuel_category_id < 800:
        # M-3 Forestry Canada. 1992 eq. 29
        percent_dead_fir = fuel_category_id % 100
        a = 170 * np.exp(-35.5/ percent_dead_fir)
    elif 800 < fuel_category_id and fuel_category_id < 1000:
        # M-4 Forestry Canada. 1992 eq. 32
        percent_dead_fir = fuel_category_id % 100
        a = 140 * np.exp(-35.5/ percent_dead_fir)

    return a

def b_coefficient(fuel_category_id):
    """Computes the rate of spread equation coefficient b based on Forestry Canada. 1992 Table 6, eqs. 30, 33"""
    b = 0
    if fuel_category_id == 1:
        # C-1
        b = 0.0649
    elif fuel_category_id == 2:
        # C-2
        b = 0.0282
    elif fuel_category_id == 3:
        # C-3
        b = 0.0444
    elif fuel_category_id == 4:
        # C-4
        b = 0.0293
    elif fuel_category_id == 5:
        # C-5
        b = 0.0697
    elif fuel_category_id == 6:
        # C-6
        b = 0.0800
    elif fuel_category_id == 7:
        # C-7
        b = 0.0305
    elif fuel_category_id == 11:
        # D-1
        b = 0.0232
    elif fuel_category_id == 12:
        # D-2
        raise Exception("No equation implemented for D-2 fuel type as it was not introduces in the Forestry Canada. 1992 report")
    elif fuel_category_id == 13:
        # D-1/2
        b = 0.0232
    elif fuel_category_id == 21:
        # S-1
        b = 0.0297
    elif fuel_category_id == 22:
        # S-2
        b = 0.0438
    elif fuel_category_id == 23:
        # S-3
        b = 0.0829
    elif fuel_category_id == 31:
        # O-1a
        b = 0.0310
    elif fuel_category_id == 32:
        # O-1b
        b = 0.0350
    elif 700 < fuel_category_id and fuel_category_id < 800:
        # M-3, Forestry Canada. 1992 eq. 30
        percent_dead_fir = fuel_category_id % 100
        b = 0.082 * np.exp(-36/ percent_dead_fir)
    elif 800 < fuel_category_id and fuel_category_id < 1000:
        # M-4 Forestry Canada. 1992 eq. 33
        b = 0.0404

    return b

def c_coefficient(fuel_category_id):
    """Computes the rate of spread equation coefficient c based on Forestry Canada. 1992 Table 6, eqs. 31, 34"""
    c = 0
    if fuel_category_id == 1:
        # C-1
        c = 4.5
    elif fuel_category_id == 2:
        # C-2
        c = 1.5
    elif fuel_category_id == 3:
        # C-3
        c = 3.0
    elif fuel_category_id == 4:
        # C-4
        c = 1.5
    elif fuel_category_id == 5:
        # C-5
        c = 4.0
    elif fuel_category_id == 6:
        # C-6
        c = 3.0
    elif fuel_category_id == 7:
        # C-7
        c = 2.0
    elif fuel_category_id == 11:
        # D-1
        c = 1.6
    elif fuel_category_id == 12:
        # D-2
        raise Exception("No equation implemented for D-2 fuel type as it was not introduces in the Forestry Canada. 1992 report")
    elif fuel_category_id == 13:
        # D-1/2
        c = 1.6
    elif fuel_category_id == 21:
        # S-1
        c = 1.3
    elif fuel_category_id == 22:
        # S-2
        c = 1.7
    elif fuel_category_id == 23:
        # S-3
        c = 3.2
    elif fuel_category_id == 31:
        # O-1a
        c = 1.4
    elif fuel_category_id == 32:
        # O-1b
        c = 1.7
    elif 700 < fuel_category_id and fuel_category_id < 800:
        # M-3, Forestry Canada. 1992 eq. 31
        percent_dead_fir = fuel_category_id % 100
        c = 1.698 - 0.00303 * percent_dead_fir
    elif 800 < fuel_category_id and fuel_category_id < 1000:
        # M-4 Forestry Canada. 1992 eq. 34
        percent_dead_fir = fuel_category_id % 100
        c = 3.02 * np.exp(-0.00714 * percent_dead_fir)

    return c

def rate_of_spread_initial(fuel_category_id, fine_fuel_moisture_code):
    """Computes the initial spread rate without build up index effect based on Forestry Canada. 1992 eqs. 26, 27, 28"""
    rsi = 0
    if fuel_category_id in (1, 2, 3, 4, 5, 6, 7, 11, 13, 21, 22, 23, 31, 32):
        # C-1, C-2, C-3, C-4, C-5, C-6, C-7, D-1, D-1/2, S-1, S-2, S-3, O-1a, O-1b, Forestry Canada. 1992 eq. 26
        rsi = a_coefficient(fuel_category_id) * (1 - np.exp(-b_coefficient(fuel_category_id) * initial_spread_index_no_slope(fine_fuel_moisture_code))) ** c_coefficient(fuel_category_id)
    elif (400 < fuel_category_id and fuel_category_id < 500):
        # M-1, M-1/2 Forestry Canada. 1992 eq. 27
        percent_conifer = fuel_category_id % 100
        percent_hardwood = 100 - percent_conifer
        rsi = (percent_conifer / 100 * rate_of_spread_initial(2, fine_fuel_moisture_code) + percent_hardwood / 100 * rate_of_spread_initial(11, fine_fuel_moisture_code))
    elif 500 < fuel_category_id and fuel_category_id < 700:
        # M-2 Forestry Canada. 1992 eq. 28
        percent_conifer = fuel_category_id % 100
        percent_hardwood = 100 - percent_conifer
        rsi = (percent_conifer / 100 * rate_of_spread_initial(2, fine_fuel_moisture_code) + 0.2 * percent_hardwood / 100 * rate_of_spread_initial(11, fine_fuel_moisture_code))
    elif 700 < fuel_category_id and fuel_category_id < 1000:
        # M-3, M-4, eq. 26
        rsi = a_coefficient(fuel_category_id) * (1 - np.exp(-b_coefficient(fuel_category_id) * initial_spread_index_no_slope(fine_fuel_moisture_code))) ** c_coefficient(fuel_category_id)
    return rsi

def rate_of_spread_proportion(fuel_category_id):
    """Returns the (constant) proportion of maximum rate of spread at build up index 50 based on Forestry Canada. 1992 Table 7"""
    q = 0
    if fuel_category_id == 1:
        # C-1
        q = 0.90
    elif fuel_category_id == 2:
        # C-2
        q = 0.70
    elif fuel_category_id == 3:
        # C-3
        q = 0.75
    elif fuel_category_id in (4, 5, 6):
        # C-4, C-5, C-6
        q = 0.80
    elif fuel_category_id == 7:
        # C-7
        q = 0.85
    elif fuel_category_id in (11, 13):
        # D-1, D-1/2
        q = 0.90
    elif fuel_category_id in (21, 22, 23):
        # S-1, S-2, S-3
        q = 0.75
    elif fuel_category_id in (31, 32):
        # O-1a, O-1b
        q = 1.00
    elif 400 < fuel_category_id and fuel_category_id < 1000:
        # M-1, M-2, M-3, M-4
        q = 0.80

    if q == 0:
        print(f"[WARNING] q == 0 for {fuel_category_id}")
    return q


def buildup_index_0(fuel_category_id):
    """Returns the (constant) average build up index based on Forestry Canada. 1992 Table 7"""
    bui0 = 0
    if fuel_category_id == 1:
        # C-1
        bui0 = 72
    elif fuel_category_id == 2:
        # C-2
        bui0 = 64
    elif fuel_category_id == 3:
        # C-3
        bui0 = 62
    elif fuel_category_id == 4:
        # C-4
        bui0 = 66
    elif fuel_category_id == 5:
        # C-5
        bui0 = 56
    elif fuel_category_id == 6:
        # C-6
        bui0 = 62
    elif fuel_category_id == 7:
        # C-7
        bui0 = 106
    elif fuel_category_id in (11, 13):
        # D-1, D-1/2
        bui0 = 32
    elif fuel_category_id == 21:
        # S-1
        bui0 = 38
    elif fuel_category_id == 22:
        # S-2
        bui0 = 63
    elif fuel_category_id == 23:
        # S-3
        bui0 = 31
    elif fuel_category_id in (31, 32):
        # O-1a, O-1b
        bui0 = 1
    elif 400 < fuel_category_id and fuel_category_id < 1000:
        # M-1, M-2, M-3, M-4
        bui0 = 50
    return bui0

def buildup_effect(fuel_category_id, buildup_index):
    """Computes the buildup effect on spread rate based on Forestry Canada. 1992 eq. 54"""
    be = np.exp(50 * np.log(rate_of_spread_proportion(fuel_category_id)) * (1 / buildup_index - 1 / buildup_index_0(fuel_category_id)))
    return be

def rate_of_spread_no_wind(fuel_category_id, fine_fuel_moisture_code, buildup_index):
    """Computes the surface rate of spread based on Forestry Canada. 1992 eq. 55"""
    ros = rate_of_spread_initial(fuel_category_id, fine_fuel_moisture_code) * buildup_effect(fuel_category_id, buildup_index)
    return ros
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
    print(f"FFMC {ffmc} is moisture content {fine_fuel_moisture_content(ffmc) / 100}")
    with open(crosswalk_path, "r") as crosswalk:
        crosswalk_data = crosswalk.readlines()[1:]
        for line in crosswalk_data:
            cad_id, _, _ = line.strip().split(",")
            cad_id = int(cad_id.strip())

            print(f"{cad_id}:")
            try:
                sfc = surface_fuel_consumption(cad_id, ffmc, bui)
                print(f"    sfc: {sfc}")
            except Exception as e:
                print(e)
            try:
                ros = rate_of_spread_no_wind(cad_id, ffmc, bui)
                print(f"    ros: {ros}")
            except Exception as e:
                print(e)
                
