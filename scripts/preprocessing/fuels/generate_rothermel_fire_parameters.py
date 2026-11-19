import os
import numpy as np
import matplotlib.pyplot as plt
out_path = os.environ["PCB_OUT_DIR"]
os.system(f"python {os.environ['PCB_OVERWRITE_PROFILE_VARS']}")


path = f"{out_path}"
fbp_json_path = f"{path}/profile/fbp.json"

# Rothermel. 1972 Table 2
HEAT_CONSTANT = 8000 # btu / lb
FIRE_DRIVEN_WIND_AMPLIFICATION = 1.3
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

def wind_factor(surface_area_volume_ratio, fuel_depth, initial_fuel_loading, particle_density, wind_speed):
    """Computes the Rothermel rate of spread equation based on Rothermel. 1972 eqs. 47, 48, 49, 50, as given in Andrews 2018 Table 3"""
    C = 7.47 * np.exp(-0.133 * surface_area_volume_ratio ** 0.55)
    B = 0.025260 * surface_area_volume_ratio ** 0.54
    E = 0.715 * np.exp(-3.54e-4 * surface_area_volume_ratio) 
    beta = mean_packing_ratio(fuel_depth, initial_fuel_loading, particle_density)
    beta_op = optimum_packing_ratio(surface_area_volume_ratio)
    phi_w = C * wind_speed ** B * (beta / beta_op) ** -E 
    return phi_w

def rate_of_spread_no_slope(surface_area_volume_ratio, fuel_depth, initial_fuel_loading, particle_density, effective_mineral_content, total_mineral_content, fuel_moisture, extinction_fuel_moisture, wind_speed):
    """Computes the Rothermel rate of spread equation with no slope adjustment based on Rothermel. 1972 eq. 52, as given in Andrews 2018 Table 3"""
    i_r = reaction_intensity(surface_area_volume_ratio, fuel_depth, initial_fuel_loading, particle_density, effective_mineral_content, total_mineral_content, fuel_moisture, extinction_fuel_moisture)
    xi = propagating_flux_ratio(surface_area_volume_ratio, fuel_depth, initial_fuel_loading, particle_density)
    rho_b = oven_dry_bulk_density(fuel_depth, initial_fuel_loading)
    epsilon = effective_heating_number(surface_area_volume_ratio)
    q_ig = preignition_heat(fuel_moisture)
    phi_w = wind_factor(surface_area_volume_ratio, fuel_depth, initial_fuel_loading, particle_density, wind_speed)
    r_0 = (i_r * xi * (1 + phi_w)) / (rho_b * epsilon * q_ig)
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

        fuel_moisture = float(input("Enter the fuel moisture fraction as a fraction (a good default is 0.1): "))
        wind_speed = float(input("Enter the mean sustained wind speed in kmh (a good default is 10 kmh): "))
        wind_speed = wind_speed * 1000 / 18.288 # foot hour per kilometre minute
        for category_name, category_data in d.items():
            rate_of_spread = category_data["ros"] / 0.3048 # metre per feet

            if rate_of_spread == 0:
                continue
            if "adjusted_fgi" in category_data:
                initial_fuel_loading = category_data["adjusted_fgi"]
            else:
                initial_fuel_loading = category_data["fgi"]
            initial_fuel_loading = initial_fuel_loading * 0.3048**2 * 2.205 # (metre per feet)^2 * (pounds per kilogram)
            surface_area_volume_ratio = category_data["savr"]
            particle_density = category_data["fueldens"]
            extinction_fuel_moisture = category_data["fuelmce"]
            total_mineral_content = category_data["st"]
            effective_mineral_content = category_data["se"]
            windrf = category_data["windrf"]
            fuel_depth = category_data["fueldepthm"]

            reduced_wind_speed = wind_speed * windrf
            print(f"Using a windrf wind speed of {reduced_wind_speed/(1000 / 18.288):.4} kmh")
            reduced_wind_speed *= FIRE_DRIVEN_WIND_AMPLIFICATION
            print(f"Using a fire driven wind speed of {reduced_wind_speed/(1000 / 18.288):.4} kmh")
            def rate_of_spread_solve(fuel_depth):
                return rate_of_spread_no_slope(surface_area_volume_ratio, fuel_depth, initial_fuel_loading, particle_density, effective_mineral_content, total_mineral_content, fuel_moisture, extinction_fuel_moisture, reduced_wind_speed) - rate_of_spread

            from scipy.optimize import brentq

            depths = np.geomspace(0.05, 50, 1000)                  # feet
            resid = np.array([rate_of_spread_solve(d) for d in depths])

            roots = [brentq(rate_of_spread_solve, depths[i], depths[i + 1])
                    for i in range(len(depths) - 1)
                    if np.isfinite(resid[i]) and np.isfinite(resid[i + 1]) and resid[i] * resid[i + 1] < 0]

            if roots:
                for r in roots:
                    print(f"{category_name}: fueldepthm = {r * 0.3048:.4f} m")
            else:
                best = depths[np.nanargmin(np.abs(resid))]
                print(f"{category_name}: no root, closest at fueldepthm = {best * 0.3048:.4f} m")
            print(f"{category_name}: fueldepthm +/=/- 50% = {fuel_depth*0.5:.4f} / {fuel_depth:.4f} / {fuel_depth*1.5:.4f} m")

            wind = np.linspace(5, 20, 100)
            plt.figure()
            rate_of_spread_array = [rate_of_spread_no_slope(surface_area_volume_ratio, r, initial_fuel_loading, particle_density, effective_mineral_content, total_mineral_content, fuel_moisture, extinction_fuel_moisture, w * (1000 / 18.288) * windrf) * 0.3048 for w in wind]
            plt.plot(wind, rate_of_spread_array)
            plt.axhline(rate_of_spread *  0.3048)
            plt.axvline(wind_speed/(1000 / 18.288))
            plt.axvline(wind_speed/(1000 / 18.288)*.667, ls = "--")
            plt.axvline(wind_speed/(1000 / 18.288)*1.33, ls = "--")
            plt.ylim(0, 17.5)
            plt.xlabel("Wind (kmh)")
            plt.ylabel(f"Rate of Spread (m)")
            plt.savefig(f"{out_path}/output/fuels/rate_of_spread_curve_fbfm{category_name}.png")