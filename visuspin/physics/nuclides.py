"""
Nuclide database: gyromagnetic ratio, spin quantum number, natural abundance.

Values are standard literature gyromagnetic ratios (rad s^-1 T^-1), consistent
with IUPAC-recommended tables (see e.g. Harris et al., Pure Appl. Chem. 73,
1795 (2001)). Spin quantum numbers and natural abundances from standard
nuclear data tables.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Nuclide:
    symbol: str          # e.g. "1H"
    gamma: float          # rad s^-1 T^-1
    spin: float           # nuclear spin quantum number I
    abundance: float      # natural abundance, %

    @property
    def mass_number(self) -> int:
        digits = "".join(ch for ch in self.symbol if ch.isdigit())
        return int(digits)

    @property
    def element(self) -> str:
        return "".join(ch for ch in self.symbol if ch.isalpha())

    @property
    def is_half_integer_quadrupolar(self) -> bool:
        """True for spin > 1/2 with a distinguished +1/2<->-1/2 central transition
        (half-integer spin). Integer-spin quadrupolar nuclei (e.g. 2H, I=1) have
        no such transition."""
        return self.spin > 0.5 and not float(self.spin).is_integer()

    def spin_label(self) -> str:
        if float(self.spin).is_integer():
            return str(int(self.spin))
        return f"{int(round(self.spin * 2))}/2"

    def formatted_symbol(self) -> str:
        sup = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
               "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}
        digits = "".join(ch for ch in self.symbol if ch.isdigit())
        return "".join(sup[d] for d in digits) + self.element


# Standard literature values. gamma in rad s^-1 T^-1.
NUCLIDES: dict[str, Nuclide] = {
    n.symbol: n for n in [
        Nuclide("1H", 267.522e6, 0.5, 99.98),
        Nuclide("2H", 41.065e6, 1.0, 0.0115),
        Nuclide("13C", 67.283e6, 0.5, 1.07),
        Nuclide("15N", -27.126e6, 0.5, 0.37),
        Nuclide("19F", 251.815e6, 0.5, 100.0),
        Nuclide("29Si", -53.190e6, 0.5, 4.68),
        Nuclide("31P", 108.394e6, 0.5, 100.0),
        Nuclide("7Li", 103.962e6, 1.5, 92.4),
        Nuclide("10B", 28.746e6, 3.0, 19.9),
        Nuclide("11B", 85.847e6, 1.5, 80.1),
        Nuclide("17O", -36.264e6, 2.5, 0.038),
        Nuclide("23Na", 70.808e6, 1.5, 100.0),
        Nuclide("27Al", 69.763e6, 2.5, 100.0),
    ]
}


def nu0_hz(nuclide: Nuclide, b0_tesla: float) -> float:
    """Larmor frequency in Hz at the given field."""
    return abs(nuclide.gamma) * b0_tesla / (2 * 3.141592653589793)
