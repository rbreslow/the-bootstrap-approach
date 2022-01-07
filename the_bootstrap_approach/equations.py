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


def relative_atmospheric_density(atmospheric_density, msl_standard_density=0.002377):
    """Calculate relative atmospheric density with :math`ρ`.

    Args:
        atmospheric_density:
            :math`ρ`, atmospheric density in slug/ft^3.
        msl_standard_density:
            MSL standard density :math:`ρ_0 = 0.002377` slug/ft^3 (Optional).

    Returns:
        relative_atmospheric_density: :math:`σ`, relative atmospheric density.
    """
    return atmospheric_density / msl_standard_density


def relative_atmospheric_density_alt(oat_f, pressure_altitude):
    """Calculate relative atmospheric density with :math:`h_p` and
    :math:`{OAT_{\degree{F}}}`.

    Args:
        oat_f:
            :math:`{OAT_{\degree{F}}}`, outside air temperature in degrees
            Fahrenheit.
        pressure_altitude:
            :math:`h_p`, pressure altitude.

    Returns:
        relative_atmospheric_density: :math:`σ`, relative atmospheric density.
    """
    # From Pg. 1 of TBA Field Guide.
    return (518.7 / (oat_f + 459.7)) * (
        1 - 6.8749 * 10 ** -6 * pressure_altitude
    ) ** 5.25625


def atmospheric_density(relative_atmospheric_density, msl_standard_density=0.002377):
    """Convert relative atmospheric density :math:`σ` to atmospheric density :math`ρ`.

    Args:
        relative_atmospheric_density:
            :math:`σ`, relative atmospheric density.
        msl_standard_density:
            MSL standard density :math:`ρ_0 = 0.002377` slug/ft^3 (Optional).

    Returns:
        atmospheric_density: :math`ρ`, atmospheric density in slug/ft^3.
    """
    return relative_atmospheric_density * msl_standard_density


def altitude_power_dropoff_factor(
    relative_atmospheric_density, altitude_engine_power_dropoff_parameter=0.12
):
    """Determine engine torque/power dropoff factor :math:`\phi`.

    Args:
        relative_atmospheric_density:
            :math:`\sigma`, relative atmospheric density.
        engine_power_altitude_dropoff_parameter:
            :math:`C`, altitude engine power dropoff parameter.

    Returns:
        :math:`\phi`, engine torque/power dropoff factor.
    """
    return (relative_atmospheric_density - altitude_engine_power_dropoff_parameter) / (
        1 - altitude_engine_power_dropoff_parameter
    )


def c_to_f(c):
    """Convert Celcius to Fahrenheit."""
    return c * (9 / 5) + 32


def f_to_c(f):
    """Convert Fahrenheit to Celcius."""
    return (f - 32) * 5 / 9


def t_isa(pressure_altitude):
    """Get ISA temperature :math:`T` in °C for :math:`h_p`."""
    return 15 - 1.98 * (pressure_altitude / 1000)


def density_altitude(pressure_altitude, oat_f):
    """Get density altitude :math:`h_ρ` from :math:`h_p` and OAT°F."""
    return (f_to_c(oat_f) - t_isa(pressure_altitude)) * 118.8 + pressure_altitude


def bootstrap_power_setting_parameter(
    engine_torque, altitude_power_dropoff_factor, base_engine_torque
):
    """Determine bootstrap power-setting parameter, Π.

    Args:
        engine_torque: :math:`M`, engine torque in ft-lbf.
        altitude_power_dropoff_factor: :math:`\phi`, engine torque/power dropoff factor.
        base_engine_torque: :math:`M_B`, base MSL-rated torque at full throttle in ft-lbf.

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
    return 1.05263 - 0.00722 * z_ratio - 0.16462 * z_ratio ** 2 - 0.18341 * z_ratio ** 3


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
        atmospheric_density * (propeller_rps ** 3) * (propeller_diameter ** 5)
    )


def power_adjustment_factor_x(total_activity_factor):
    """Power adjusment factor :math:`X` for your propeller depends on its TAF
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
    return (2 * gross_aircraft_weight ** 2) / (
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
    return g * air_speed ** 3 + h / air_speed


def power_available(eta, power):
    return eta * power


def tas(cas, relative_atmospheric_density):
    return cas / math.sqrt(relative_atmospheric_density)


def cas(tas, relative_atmospheric_density):
    return math.sqrt(relative_atmospheric_density) * tas


def kn_to_fts(kn):
    return kn / 0.5924838
