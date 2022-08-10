import math


def engine_torque(power, propeller_rps):
    """Engine torque :math:`M` depends on the following formula:

    :math:`M = P / 2\pin`

    Args:
        power: :math:`P`, power in ft-lbf/s.
        propeller_rps: :math:`n`, propeller revolutions per second.

    Returns:
        :math:`M`, engine torque in ft-lbf.
    """
    return power / (2 * math.pi * propeller_rps)


def engine_power(torque, propeller_rps):
    return 2 * math.pi * propeller_rps * torque


def relative_temperature(oat_f):
    # Temperature ratio is temperature in absolute Fahrenheit (Rankine) units (°R =
    # °F + 459.7) divided by MSL standard temperature [1, p. 7].
    return (oat_f + 459.7) / 518.7


def relative_pressure(pressure_altitude):
    # Pressure ratio is temperature in absolute Fahrenheit (Rankine) units (°R =
    # °F + 459.7) divided by MSL standard temperature [1, p. 7].
    return (1 - pressure_altitude / 145457) ** 5.25635


def relative_atmospheric_density(pressure_altitude, oat_f):
    """Calculate relative atmospheric density with :math:`h_p` and OAT°F.

    Args:
        oat_f: OAT°F, outside air temperature in degrees Fahrenheit.
        pressure_altitude: :math:`h_p`, pressure altitude.

    Returns:
        relative_atmospheric_density: σ, relative atmospheric density.
    """
    # "Correcting" the pressure ratio for non-standard temperature yields the density
    # ratio (relative atmospheric density) [9, p. 989], [1, p. 20].
    return relative_pressure(pressure_altitude) / relative_temperature(oat_f)


def atmospheric_density(pressure_altitude, oat_f):
    """Calculate atmospheric density ρ with :math:`h_p` and OAT°F.

    Args:
        pressure_altitude: :math:`h_p`, pressure altitude.
        oat_f: OAT°F, outside air temperature in degrees Fahrenheit.

    Returns:
        atmospheric_density: ρ, atmospheric density in slugs/ft³.
    """
    # The standard MSL value of density for dry air is 0.002377 slugs/ft³ [1, p. 7].
    return relative_atmospheric_density(pressure_altitude, oat_f) * 0.002377


def altitude_power_dropoff_factor(
    relative_atmospheric_density, altitude_engine_power_dropoff_parameter=0.12
):
    """Determine engine torque/power dropoff factor :math:`\phi`.

    Args:
        relative_atmospheric_density:
            :math:`\sigma`, relative atmospheric density.
        altitude_engine_power_altitude_dropoff_parameter:
            :math:`C`, altitude engine power dropoff parameter.

    Returns:
        :math:`\phi`, engine torque/power dropoff factor.
    """
    return (relative_atmospheric_density - altitude_engine_power_dropoff_parameter) / (
        1 - altitude_engine_power_dropoff_parameter
    )


def c_to_f(c):
    """Convert Celsius to Fahrenheit."""
    return c * (9 / 5) + 32


def f_to_c(f):
    """Convert Fahrenheit to Celsius."""
    return (f - 32) * 5 / 9


def british_standard_temperature(altitude):
    """Get standard temperature :math:`T_S(h)` at altitude :math:`h` above mean
    sea level.

    Args:
        altitude: :math:`h`, any altitude above mean sea level.

    Returns:
        :math:`T_S(h)`, standard temperature in British engineering units, °F.

    """
    return 59 - 0.003566 * altitude


def metric_standard_temperature(altitude):
    """Get standard temperature :math:`T_S(h)` at altitude :math:`h` above mean
    sea level.

    Args:
        altitude: :math:`h`, any altitude above mean sea level.

    Returns:
        :math:`T_S(h)`, standard temperature in metric units, °C.

    """
    return 15 - 0.001981 * altitude


def density_altitude(pressure_altitude, oat_f):
    """Get density altitude :math:`h_ρ` with :math:`h_p` and OAT°F.

    Args:
        pressure_altitude: :math:`h_p`, pressure altitude.
        oat_f: OAT°F, outside air temperature in degrees Fahrenheit.

    Returns:
        density_altitude: :math:`h_p`, density altitude.
    """
    return 145457 * (
        1 - relative_atmospheric_density(pressure_altitude, oat_f) ** 0.23494
    )


def bootstrap_power_setting_parameter(
    engine_torque, altitude_power_dropoff_factor, base_engine_torque
):
    """Determine bootstrap power-setting parameter, Π.

    Args:
        engine_torque: :math:`M`, engine torque in ft-lbf.
        altitude_power_dropoff_factor: :math:`\phi`, engine torque/power dropoff factor.
        base_engine_torque: :math:`M_B`, base MSL-rated torque at full throttle in
        ft-lbf.

    Returns:
        :math:`Π`, bootstrap power-setting parameter.
    """
    return engine_torque / (altitude_power_dropoff_factor * base_engine_torque)


def sdef_t(z_ratio):
    """Slowdown efficiency factor for the tractor propeller :math:`{SDEF}_T` was
    adapted from the 1936 graphs made by Walter Stuart Diehl from British and
    American experiments.

    Args:
        z_ratio: :math:`Z`, ratio of fuselage diameter to propeller diameter.

    Returns:
        :math:`{SDEF}`, slowdown efficiency factor for the tractor propeller.
    """
    return 1.05263 - 0.00722 * z_ratio - 0.16462 * z_ratio**2 - 0.18341 * z_ratio**3


def propeller_advance_ratio(air_speed, propeller_rps, propeller_diameter):
    """Propeller advance ratio :math:`J` depends on the following formula:

    :math:`J = V/nd`

    Args:
        air_speed: Air speed in ft/sec.
        propeller_rps: :math:`n`, propeller revolutions per second.
        propeller_diameter: propeller diameter in ft.

    Returns:
        :math:`J`, propeller advance ratio.
    """
    return air_speed / (propeller_rps * propeller_diameter)


def propeller_power_coefficient(
    power, atmospheric_density, propeller_rps, propeller_diameter
):
    """Propeller power coefficient :math:`C_P` depends on the following formula:

    :math:`C_P = P/\\rhon^3d^5`

    Args:
        power: :math:`P`, power in ft-lbf/s.
        atmospheric_density: :math:`\\rho`, atmospheric density in slug/ft^3.
        propeller_rps: :math:`n`, propeller revolutions per second.
        propeller_diameter: propeller diameter in ft.

    Returns:
        :math:`C_P`, propeller power coefficient.
    """
    return power / (
        atmospheric_density * (propeller_rps**3) * (propeller_diameter**5)
    )


def power_adjustment_factor_x(total_activity_factor):
    """Power adjustment factor :math:`X` for your propeller depends on its TAF
    according to the (curve-fit) formula:

    :math:`X = 0.001515 {TAF} - 0.0880`

    Args:
        total_activity_factor:
            :math:`{TAF}`, the propeller total activity factor.

    Returns:
        :math:`X`, power adjustment factor.
    """
    return 0.001515 * total_activity_factor - 0.088


def G(atmospheric_density, reference_wing_area, parasite_drag_coefficient):
    """Calculate composite bootstrap parameter :math:`G`."""
    return 0.5 * atmospheric_density * reference_wing_area * parasite_drag_coefficient


def H(
    gross_aircraft_weight,
    atmospheric_density,
    reference_wing_area,
    oswald_airplane_efficiency_factor,
    wing_aspect_ratio,
):
    """Calculate composite bootstrap parameter :math:`H`."""
    return (2 * gross_aircraft_weight**2) / (
        atmospheric_density
        * reference_wing_area
        * math.pi
        * oswald_airplane_efficiency_factor
        * wing_aspect_ratio
    )


def power_required(g, h, air_speed):
    """Determine power required :math:`P_{re}` to overcome the total drag force
    at air speed :math:`V`."""
    # $P_{re} = {GV}^3 + H/V$
    return g * air_speed**3 + h / air_speed


def power_available(eta, power):
    return eta * power


def tas(cas, relative_atmospheric_density):
    return cas / math.sqrt(relative_atmospheric_density)


def cas(tas, relative_atmospheric_density):
    return math.sqrt(relative_atmospheric_density) * tas


def kn_to_fts(kn):
    return kn * (6076.115 / 3600)


def fts_to_kn(fts):
    return fts * (3600 / 6076.115)


def fuel_gal_to_lbf(fuel_gal, oat_f):
    """Convert gallons per hour of AvGas to pounds per hour, considering
    temperature variation."""
    # For 100/130 aviation gasoline: Fuel lbf/U.S. gall = 6.077 - 0.00409 x °F.
    # [1, p. 122].
    fuel_lbf_per_gal = 6.077 - (0.00409 * oat_f)
    return fuel_gal * fuel_lbf_per_gal


def fuel_lbf_to_gal(fuel_lbf, oat_f):
    """Convert pounds per hour of AvGas to gallons per hour per, considering
    temperature variation."""
    # For 100/130 aviation gasoline: Fuel lbf/U.S. gall = 6.077 - 0.00409 x °F.
    # [1, p. 122].
    fuel_lbf_per_gal = 6.077 - (0.00409 * oat_f)
    return fuel_lbf / fuel_lbf_per_gal


def ft_lbfs_to_hp(ft_lbfs):
    return ft_lbfs / 550


def scale_v_speed_by_weight(speed_at_old_weight, old_weight, new_weight):
    return speed_at_old_weight + speed_at_old_weight / (2 * new_weight) * (
        new_weight - old_weight
    )
