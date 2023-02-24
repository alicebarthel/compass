from compass.testcase import TestCase
from compass.ocean.tests.mitgcm_baroclinic_gyre.initial_state import InitialState
from compass.mesh import QuasiUniformSphericalMeshStep
from compass.ocean.tests.mitgcm_baroclinic_gyre.cull_mesh import CullMesh

class GyreTestCase(TestCase):
    """
    A class to define the MITgcm baroclinic gyre test cases

    Attributes
    ----------
    resolution : str
        The resolution of the test case
    """

    def __init__(self, test_group, resolution):
        """
        Create the test case

        Parameters
        ----------
        test_group : compass.ocean.tests.mitgcm_baroclinic_gyre.MitgcmBaroclinicGyre
            The test group that this test case belongs to

        resolution : str
            The resolution of the test case
        """
        name = 'performance'
        self.resolution = resolution
        subdir = f'{resolution}/{name}'
        super().__init__(test_group=test_group, name=name,
                         subdir=subdir)

        self.add_step(QuasiUniformSphericalMeshStep(
            test_case=self, cell_width=int(resolution[:-2])))
        self.add_step(CullMesh(test_case=self))
        self.add_step(
            InitialState(test_case=self, resolution=resolution))

    def configure(self):
        """
        Set config options for the test case
        """
        config = self.config
        config.add_from_package('compass.mesh', 'mesh.cfg')
