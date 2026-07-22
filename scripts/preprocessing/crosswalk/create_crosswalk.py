# Creates a crosswalk using the crosstab csv created from find_crosstab.py
# If the Canadian FBP Fuel Type has at least 40% pluralirty with one US FBFM category, and no other FBFM category is within 15% of the leading category, the crosswalk is considered safe.
# If the Canadian FBP Fuel Type has less than 40% pluralirty with one US FBFM category, or an FBFM category is within 15% of the leading category, the crosswalk will be created but a warning will be printed.
# If the Canadian FBP Fuel Type has its leading two FBFM categories within 7.5% of eachother, the crosswalk will be to -9999 (NoData) and require manual review.
# If the Canadian FBP Fuel Type has less than 1000 counts of FBFM data or its leading category has less than 500 counts, the crosswalk will be to -9999 (NoData) and require manual review.



import sys
import os
import numpy as np

def save_crosswalk(crosswalk: dict, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    s = "Candian ID, Candian Name, US ID\n" 
    for en, val in crosswalk.items():
        s += f"{en}, {val['name']}, {val['USIndex']}\n"
    
    with open(path, 'w') as f:
        f.write(s)


fbp_table_text = ""

with open(f'{sys.argv[1]}/data/FBP_fueltypes_Canada_30m/FBP30_ColorTable.txt', 'r') as f:
    fbp_table_text = f.read()
base_crosswalk = {}

for line in fbp_table_text.strip().split('\n'):
    parts = line.split(maxsplit=5)
    
    if len(parts) == 6:
        fuel_id = int(parts[0])
        description = parts[5].strip()
        base_crosswalk[fuel_id] = {}
        base_crosswalk[fuel_id]["name"] = description
        base_crosswalk[fuel_id]["USIndex"] = -9999


crosstab_dir = f"{sys.argv[1]}/output/crosstab"

profiles = os.scandir(crosstab_dir)
for profile in profiles:
    if not profile.is_dir():
        continue
    
    label = profile.name
    csvs = os.scandir(profile.path)
    for csv in csvs:
        if not csv.is_file() or not csv.name.endswith('.csv'):
            continue
        
        name = csv.name
        crosstab_text = ""
        crosswalk = base_crosswalk.copy()
        with open(csv.path) as f:
            crosstab_text = f.read().strip()
        
        if not crosswalk or crosswalk == "\"\"":
            save_crosswalk(crosswalk, f"{sys.argv[1]}/output/crosswalk/{label}/{name}")

        crosstab = crosstab_text.split("\n")
        headers = crosstab[0].strip().split(",")[1::]
        crosstab = crosstab[1::]

        for en in crosstab:
            if not en.strip():
                continue
            cols = [c.strip() for c in en.split(",")]
            i = int(cols[0])
            counts = np.array([int(c) for c in cols[1::]])
            percents = counts / np.sum(counts)

            sorted_indices = np.argsort(percents)

            # The highest is the last item, the second highest is the second to last
            max_percent_idx = sorted_indices[-1]
            second_max_percent_idx = sorted_indices[-2]

            if percents[max_percent_idx] > .4 and abs(percents[max_percent_idx] - percents[second_max_percent_idx]) > .10:
                crosswalk[i]["USIndex"] = headers[max_percent_idx]
            elif  abs(percents[max_percent_idx] - percents[second_max_percent_idx]) > .005 and np.sum(counts) >= 1000 and counts[max_percent_idx] >= 500:
                crosswalk[i]["USIndex"] = headers[max_percent_idx]
                print(f"[{label}] Crosswalk: {name} Candian FBP Fuel Type {crosswalk[i]['name']} ({i}) was assigned to US fuel type {headers[max_percent_idx]} but it may also be {headers[second_max_percent_idx]} ({headers[max_percent_idx]}: {percents[max_percent_idx]*100:.1f}% and {headers[second_max_percent_idx]}: {percents[second_max_percent_idx]*100:.1f}%). ")
            else: 
                print(f"[{label}] Crosswalk: {name} Candian FBP Fuel Type {crosswalk[i]['name']} ({i}) was not assigned due to uncertain results") 

        save_crosswalk(crosswalk, f"{sys.argv[1]}/output/crosswalk/{label}/{name}")