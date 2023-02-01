from compass.testgroup import TestGroup
from compass.ocean.tests.mitgcm_baroclinic_gyre.gyre_test_case import GyreTestCase


class MitgcmBaroclinicGyre(TestGroup):
    """
    A test group for MITgcm baroclinic gyre test cases
    """
    def __init__(self, mpas_core):
        """
        mpas_core : compass.MpasCore
            the MPAS core that this test group belongs to
        """
        super().__init__(mpas_core=mpas_core, name='mitgcm_baroclinic_gyre')

        for resolution in ['80km']:
            self.add_test_case(
                GyreTestCase(test_group=self, resolution=resolution))


