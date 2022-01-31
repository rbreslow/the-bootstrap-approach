from abc import ABC, abstractmethod
import math

from the_bootstrap_approach.dataplate import DataPlate
from the_bootstrap_approach.equations import (
    G,
    H,
    density_altitude,
    atmospheric_density,
    altitude_power_dropoff_factor,
)
from the_bootstrap_approach.mixture import Mixture


class Conditions(ABC):
    def __init__(
        self,
        dataplate: DataPlate,
        gross_aircraft_weight,
        pressure_altitude,
        oat_f,
        mixture: Mixture,
        engine_rpm,
    ):
        self.dataplate = dataplate
        self.gross_aircraft_weight = gross_aircraft_weight
        self.pressure_altitude = pressure_altitude
        self.oat_f = oat_f
        self.mixture = mixture
        self.engine_rpm = engine_rpm
        self.g = G(
            self.atmospheric_density,
            self.dataplate.reference_wing_area,
            self.dataplate.parasite_drag_coefficient,
        )
        self.h = H(
            self.gross_aircraft_weight,
            self.atmospheric_density,
            self.dataplate.reference_wing_area,
            self.dataplate.airplane_efficiency_factor,
            self.dataplate.wing_aspect_ratio,
        )

    @property
    def relative_atmospheric_density(self):
        return (
            1 - density_altitude(self.pressure_altitude, self.oat_f) / 145457
        ) ** 4.25635

    @property
    def atmospheric_density(self):
        return atmospheric_density(self.relative_atmospheric_density)

    @property
    @abstractmethod
    def power(self):
        pass

    @property
    def propeller_rps(self):
        return self.engine_rpm / 60

    @property
    def bsfc(self):
        return self.dataplate.bsfc(self.mixture)

    @property
    @abstractmethod
    def desc(self):
        """Description of the type of operating conditions (e.g., partial or
        full throttle)."""
        pass


class FullThrottleConditions(Conditions):
    @property
    def torque(self):
        # "Full-throttle torque depends on air density via
        # $M(\sigma) = \phi(\sigma)M_0 = \frac{(\sigma - C)}{(1 - C)}M_0$
        # where C is a number close to 0.12, giving the proportion of internal
        # engine losses not responsive to air density." [1, p. 231]
        return (
            altitude_power_dropoff_factor(
                self.relative_atmospheric_density,
                self.dataplate.engine_power_altitude_dropoff_parameter,
            )
            * self.dataplate.rated_full_throttle_engine_torque
        )

    @property
    def power(self):
        return (
            # First, we need to factor slower-than-full-rated RPM with $P = 2\pinM$.
            2
            * math.pi
            * self.propeller_rps
            * self.dataplate.rated_full_throttle_engine_torque
            # Then, we factor in the losses from Best Economy operation
            # (approximated from the O-540 operator's manual).
            * (0.945 if self.mixture == Mixture.BEST_ECONOMY else 1)
            # Finally, we can factor in power losses at altitude.
            * altitude_power_dropoff_factor(
                self.relative_atmospheric_density,
                self.dataplate.engine_power_altitude_dropoff_parameter,
            )
        )

    @property
    def desc(self):
        return "Full Throttle"


class PartialThrottleConditions(Conditions):
    def __init__(
        self,
        dataplate: DataPlate,
        gross_aircraft_weight,
        pressure_altitude,
        oat_f,
        mixture: Mixture,
        engine_rpm,
        power,
    ):
        super().__init__(
            dataplate,
            gross_aircraft_weight,
            pressure_altitude,
            oat_f,
            mixture,
            engine_rpm,
        )
        self._power = power

    @property
    def power(self):
        return self._power

    @property
    def desc(self):
        return "Partial Throttle"
