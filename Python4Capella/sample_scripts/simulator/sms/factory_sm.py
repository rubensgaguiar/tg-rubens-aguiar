import sys

from typing_extensions import Self

if "pytest" in sys.modules:
    from simulator.sms.sismic_sm import *
else:
    # SismicParser
    include('workspace://Python4Capella/sample_scripts/simulator/sms/sismic_sm.py')


class SMFactory:
    """
      Fábrica de Máquina de Estados
    """

    def __new__(cls, type) -> Self:
        # Fabrica o modelo solicitado
        products = {
            'sismic': SismicSM
        }
        return products[type]()
