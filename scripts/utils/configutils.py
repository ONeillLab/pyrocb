

import os
import json

out_path = os.environ["PCB_OUT_DIR"]
fbp_json_path = f"{out_path}/profile/fbp.json"

fbp = None
if os.path.isfile(fbp_json_path):
    with open(fbp_json_path, "r") as f:
        fbp = json.load(f)

def _pick(val, region):
    """Region value if present, else 'Overall', else None. Scalars pass through."""
    if isinstance(val, dict):
        if region is not None and region in val:
            return val[region]
        return val.get("Overall")
    return val

def fbp_get_val(parameter, fuel_type_id=None, species=None, region=None):
    if fbp is None:
        print("[ERROR] NO FBP file found")
        return None
    entry = fbp.get(str(fuel_type_id)) if fuel_type_id is not None else None
    if entry is not None:
        species_list = entry.get("species", [])
        # 1) the named species (region -> Overall)
        if species is not None:
            for sp in species_list:
                if sp["name"] == species:
                    v = _pick(sp.get(parameter), region)
                    if v is not None:
                        return v
                    break
        # 2) weight-averaged over the fuel type's species
        pairs = [(sp["weight"], _pick(sp.get(parameter), region)) for sp in species_list]
        pairs = [(w, v) for w, v in pairs if v is not None]
        if pairs:
            return sum(w * v for w, v in pairs) / sum(w for w, _ in pairs)
        # 3) scalar on the fuel type itself (e.g. CAD 31)
        v = _pick(entry.get(parameter), region)
        if v is not None:
            return v
    # 4) top-level "Overall" entry, if the file has one
    ov = fbp.get("Overall")
    if ov is not None:
        v = _pick(ov.get(parameter), region)
        if v is not None:
            return v
    print(f'[ERROR] No value for "{parameter}" (fuel_type_id={fuel_type_id}, species={species}, region={region})')
    return None