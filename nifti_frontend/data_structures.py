import os
import numpy as np
import weakref
import nibabel as nib

from yt.data_objects.grid_patch import \
    AMRGridPatch
from yt.geometry.grid_geometry_handler import \
    GridIndex
from yt.data_objects.static_output import \
    Dataset
from .fields import NiftiFieldInfo

class NiftiGrid(AMRGridPatch):
    id_offset = 0

    def __init__(self, id, index, level, dimensions):
        super(NiftiGrid, self).__init__(
            id, filename=index.index_filename, index=index)
        self.Parent = None
        self.Children = []
        self.Level = level
        self.ActiveDimensions = dimensions


    def __repr__(self):
        return "niftiGrid_%04i (%s)" % (self.id, self.ActiveDimensions)

class NiftiHierarchy(GridIndex):
    grid = NiftiGrid

    def __init__(self, ds, dataset_type='nifti'):
        self.dataset_type = dataset_type
        self.dataset = weakref.proxy(ds)
        # for now, the index file is the dataset!
        self.index_filename = self.dataset.parameter_filename
        self.directory = os.path.dirname(self.index_filename)
        # float type for the simulation edges and must be float64 now
        self.float_type = np.float64
        super(NiftiHierarchy, self).__init__(ds, dataset_type)


    def _detect_output_fields(self):
        # This needs to set a self.field_list that contains all the available,
        # on-disk fields. No derived fields should be defined here.
        # NOTE: Each should be a tuple, where the first element is the on-disk
        # fluid type or particle type.  Convention suggests that the on-disk
        # fluid type is usually the dataset_type and the on-disk particle type
        # (for a single population of particles) is "io".
        self.field_list = [("scan", "intensity")]

    def _count_grids(self):
        # This needs to set self.num_grids
        self.num_grids = 1

    def _parse_index(self):
        # This needs to fill the following arrays, where N is self.num_grids:
        #   self.grid_left_edge         (N, 3) <= float64
        #   self.grid_right_edge        (N, 3) <= float64
        #   self.grid_dimensions        (N, 3) <= int
        #   self.grid_particle_count    (N, 1) <= int
        #   self.grid_levels            (N, 1) <= int
        #   self.grids                  (N, 1) <= grid objects
        #   self.max_level = self.grid_levels.max()
        self.grid_left_edge[:] = [0.0, 0.0, 0.0]
        self.grid_right_edge[:] = [1.0, 1.0, 1.0]
        self.grid_dimensions[:] = self.dataset.domain_dimensions
        self.grid_levels[:] = 0
        self.max_level = 0
        self.grids = np.empty(self.num_grids, dtype='object')
        self.grids[0] = self.grid(0, self, 0, self.grid_dimensions[:,0])

    def _populate_grid_objects(self):
        for g in self.grids:
            g._prepare_grid()
            g._setup_dx()
            g.Children = []
            g.Parent = None

class NiftiDataset(Dataset):
    _index_class = NiftiHierarchy
    _field_info_class = NiftiFieldInfo

    def __init__(self, filename, dataset_type='nifti',
                 storage_filename=None,
                 units_override=None):
        self.fluid_types += ('scan',)
        super(NiftiDataset, self).__init__(filename, dataset_type,
                         units_override=units_override)
        self.storage_filename = storage_filename
        # refinement factor between a grid and its subgrid
        # self.refine_by = 2

    def _set_code_unit_attributes(self):
        # This is where quantities are created that represent the various
        # on-disk units.  These are the currently available quantities which
        # should be set, along with examples of how to set them to standard
        # values.
        #

        self.mass_unit = self.quan(1.0, "g")
        self.time_unit = self.quan(1.0, "s")
        # self.time_unit = self.quan(1.0, "s")

        l,t = self.header.get_xyzt_units()
        self.length_unit = self.quan(1.0,l)
        #
        #
        # These can also be set:
        # self.velocity_unit = self.quan(1.0, "cm/s")
        # self.magnetic_unit = self.quan(1.0, "gauss")

    def _parse_parameter_file(self):
        # This needs to set up the following items.  Note that these are all
        # assumed to be in code units; domain_left_edge and domain_right_edge
        # will be converted to YTArray automatically at a later time.
        # This includes the cosmological parameters.

        self.unique_identifier = None

        fid = nib.load(self.parameter_filename)

        # is where I store the numpy arrays?
        # or should this be the header values?
        self.parameters = {}
        self.parameters.update(fid.get_header())

        self.file_handle = fid
        self.header = fid.get_header()

        xsize, ysize, zsize, _ = (np.abs(_) for _ in fid.header.get_best_affine()[:, 3])


        self.domain_left_edge = np.array([-xsize, -ysize, -zsize])
        self.domain_right_edge = np.array([xsize, ysize, zsize])
        self.dimensionality = 3
        self.domain_dimensions = fid.shape
        self.periodicity = 0
        self.current_time = 0
        self.cosmological_simulation = 0
        self.current_redshift = 0
        self.omega_lambda = 0
        self.omega_matter = 0
        self.hubble_constant = 0



    @classmethod
    def _is_valid(self, *args, **kwargs):
        # unqiue MRI file format identifier
        try:
            return args[0].endswith(".nii") or args[0].endswith(".nii.gz")
        except:
            pass
