import sys

from typing_extensions import Self

if "pytest" in sys.modules:
    from simulator.parsers.sismic_parser import *
else:
    # SismicParser
    include(
        'workspace://Python4Capella/sample_scripts/simulator/parsers/sismic_parser.py')


class ParserFactory:
    """
      Fábrica de Parser
    """

    def __new__(cls, type) -> Self:
        # Fabrica o modelo solicitado
        products = {
            'sismic': SismicParser
        }
        return products[type]()
