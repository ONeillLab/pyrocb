import os
import numpy as np
out_path = os.environ["PCB_OUT_DIR"]
os.system(f"python {os.environ['PCB_OVERWRITE_PROFILE_VARS']}")


path = f"{out_path}"
fbp_json_path = f"{path}/profile/fbp.json"

# Rothermel. 1972 Table 2
HEAT_CONSTANT = 8000 # btu / lb

def maximum_reaction_velocity(surface_area_volume_ratio):
    """Computes maximum reaction velocity based on Rothermel. 1972 eq. 36, as given in Andrews 2018 Table 3"""
    gamma_prime_max = (surface_area_volume_ratio ** 1.5) * (495 + 0.05940 * surface_area_volume_ratio ** 1.5) ** -1
    return gamma_prime_max

def mean_packing_ratio(fuel_depth, initial_fuel_loading, particle_density):
    """Computes mean packing ratio based on Rothermel. 1972 eq. 31, as given in Andrews 2018 Table 3"""
    beta = (1 / fuel_depth) * (initial_fuel_loading / particle_density)
    return beta

def optimum_packing_ratio(surface_area_volume_ratio):
    """Computes optimum packing ratio based on Rothermel. 1972 eq. 37, as given in Andrews 2018 Table 3"""
    beta_op = 3.348 * (surface_area_volume_ratio) ** -0.8189
    return beta_op

def optimum_reaction_velocity(surface_area_volume_ratio, fuel_depth, initial_fuel_loading, particle_density):
    """Computes optimum reaction velocity based on Rothermel. 1972 eqs. 38, 39, as given in Andrews 2018 Table 3"""
    gamma_prime_max = maximum_reaction_velocity(surface_area_volume_ratio)
    beta = mean_packing_ratio(fuel_depth, initial_fuel_loading, particle_density)
    beta_op = optimum_packing_ratio(surface_area_volume_ratio)
    A = 133 * surface_area_volume_ratio ** -0.7913 # Rothermel. 1972 eq. 39, as given in Andrews 2018 Table 3
    gamma_prime = gamma_prime_max * (beta / beta_op) ** A * np.exp(A * (1 - (beta / beta_op))) # Rothermel. 1972 eq. 38, as given in Andrews 2018 Table 3
    return gamma_prime

def net_fuel_load(initial_fuel_loading, total_mineral_content):
    """Computes net fuel load based on Rothermel. 1972 eq. 24, as given in Andrews 2018 Table 3"""
    w_n = initial_fuel_loading * (1 - total_mineral_content)
    return w_n

def moisture_damping_coefficient(fuel_moisture, extinction_fuel_moisture):
    """Computes fuel moisture coefficient based on Rothermel. 1972 eq. 29, as given in Andrews 2018 Table 3"""
    r_m = min(fuel_moisture / extinction_fuel_moisture, 1)
    eta_m = 1 - 2.59 * r_m + 5.11 * r_m ** 2 - 3.52 * r_m ** 3
    return eta_m

def mineral_damping_coefficient(effective_mineral_content):
    """Computes mineral damping coefficient based on Rothermel. 1972 eq. 30, as given in Andrews 2018 Table 3"""
    eta_s = 0.174 * effective_mineral_content ** -0.19
    return min(eta_s, 1)

def reaction_intensity(surface_area_volume_ratio, fuel_depth, initial_fuel_loading, particle_density, effective_mineral_content, total_mineral_content, fuel_moisture, extinction_fuel_moisture):
    """Computes reaction intensity based on Rothermel. 1972 eq. 27, as given in Andrews 2018 Table 3"""
    gamma_prime = optimum_reaction_velocity(surface_area_volume_ratio, fuel_depth, initial_fuel_loading, particle_density)
    w_n = net_fuel_load(initial_fuel_loading, total_mineral_content)
    eta_m = moisture_damping_coefficient(fuel_moisture, extinction_fuel_moisture)
    eta_s = mineral_damping_coefficient(effective_mineral_content)
    i_r = gamma_prime * w_n * eta_m * eta_s * HEAT_CONSTANT
    return i_r

def propagating_flux_ratio(surface_area_volume_ratio, fuel_depth, initial_fuel_loading, particle_density):
    """Computes propagating flux ratio based on Rothermel. 1972 eq. 42, as given in Andrews 2018 Table 3"""
    beta = mean_packing_ratio(fuel_depth, initial_fuel_loading, particle_density)
    xi = (192 + 0.2595 * surface_area_volume_ratio) ** -1 * np.exp((beta + 0.1) * (0.792 + 0.681 * surface_area_volume_ratio ** 0.5))
    return xi

def oven_dry_bulk_density(fuel_depth, initial_fuel_loading):
    """Computes oven dry bulk density based on Rothermel. 1972 eq. 40, as given in Andrews 2018 Table 3"""
    rho_b = initial_fuel_loading / fuel_depth
    return rho_b

def effective_heating_number(surface_area_volume_ratio):
    """Computes effective heating number based on Rothermel. 1972 eq. 14, as given in Andrews 2018 Table 3"""
    epsilon = np.exp(-138  / surface_area_volume_ratio)
    return epsilon

def preignition_heat(fuel_moisture):
    """Computes heat of preignition based on Rothermel. 1972 eq. 12, as given in Andrews 2018 Table 3"""
    q_ig = 250 + 1116 * fuel_moisture
    return q_ig

def rate_of_spread_no_slope(surface_area_volume_ratio, fuel_depth, initial_fuel_loading, particle_density, effective_mineral_content, total_mineral_content, fuel_moisture, extinction_fuel_moisture):
    """Computes the Rothermel rate of spread equation based on Rothermel. 1972 eq. 52, as given in Andrews 2018 Table 3"""
    i_r = reaction_intensity(surface_area_volume_ratio, fuel_depth, initial_fuel_loading, particle_density, effective_mineral_content, total_mineral_content, fuel_moisture, extinction_fuel_moisture)
    xi = propagating_flux_ratio(surface_area_volume_ratio, fuel_depth, initial_fuel_loading, particle_density)
    rho_b = oven_dry_bulk_density(fuel_depth, initial_fuel_loading)
    epsilon = effective_heating_number(surface_area_volume_ratio)
    q_ig = preignition_heat(fuel_moisture)

    r_0 = (i_r * xi) / (rho_b * epsilon * q_ig)
    return r_0

if __name__ == "__main__":
    us_params_path = f"{out_path}/profile/us_params.csv"

    with open(us_params_path, "r") as f:
        lines = f.readlines()
        headers = lines[0].strip().split(",")[1:-1:]
        headers = [h.strip() for h in headers]
        d = {}
        for category in headers:
            d[category] = {}
        for line in lines[1::]:
            line = line.split(",")
            line = [l.strip() for l in line]
            for i, category in enumerate(line[1:-1:]):
                d[headers[i]][line[0]] = float(category)

        fuel_moisture = float(input("Enter the fuel moisture fraction as a fraction (a good default is 0.1): ") )
        for category_name, category_data in d.items():
            rate_of_spread = category_data["ros"] / 0.3048

            if rate_of_spread == 0:
                continue
            if "adjusted_fgi" in category_data:
                initial_fuel_loading = category_data["adjusted_fgi"]
            else:
                initial_fuel_loading = category_data["fgi"]
            initial_fuel_loading = initial_fuel_loading * 0.3048**2 * 2.205
            surface_area_volume_ratio = category_data["savr"]
            particle_density = category_data["fueldens"]
            extinction_fuel_moisture = category_data["fuelmce"]
            total_mineral_content = category_data["st"]
            effective_mineral_content = category_data["se"]
            fuel_depth = category_data["fueldepthm"]

            def rate_of_spread_solve(fuel_depth):
                return rate_of_spread_no_slope(surface_area_volume_ratio, fuel_depth, initial_fuel_loading, particle_density, effective_mineral_content, total_mineral_content, fuel_moisture, extinction_fuel_moisture) - rate_of_spread

            from scipy.optimize import root_scalar, minimize_scalar
            try:
                sol = root_scalar(rate_of_spread_solve, bracket=[0.05, 50],            # depth in feet
                              method="brentq", xtol=1e-9)
                print(f"{category_name}: fueldepthm = {sol.root * 0.3048:.4f} m (converged: {sol.converged})")
            except Exception as e:
                def f(fuel_depth):
                    return np.abs(rate_of_spread_solve(fuel_depth))
                sol = minimize_scalar(f, bounds=(0.05, 50), method='bounded')
                print(e)
                print(f"{category_name}: Closest at fueldepthm = {sol.x  * 0.3048:.4f} m (ros = {sol.fun * 0.3048:.4f} m/s)")
            print(f"{category_name}: fueldepthm +/=/- 50% = {fuel_depth*0.5:.4f} / {fuel_depth:.4f} / {fuel_depth*1.5:.4f} m")