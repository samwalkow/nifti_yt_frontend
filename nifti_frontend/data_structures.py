

class niftiGrid(AMRGridPatch):
    id_offset = 0

    def __init__(self, id, index, level, dimensions):
        super(niiGrid, self).__init__(
            id, filename=index.index_filename, index=index)
        self.Parent = None
        self.Children = []
        self.Level = level
        self.ActiveDimensions = dimensions

    def __repr__(self):
        return "niiGrid_%04i (%s)" % (self.id, self.ActiveDimensions)

class niftiDataset(Dataset):
    _index_class = SkeletonHierarchy
    _field_info_class = SkeletonFieldInfo

    def __init__(self, filename, dataset_type='nifti',
                 storage_filename=None,
                 units_override=None):
        self.fluid_types += ('skeleton',)
        super(SkeletonDataset, self).__init__(filename, dataset_type,
                         units_override=units_override)
        self.storage_filename = storage_filename
        # refinement factor between a grid and its subgrid
        # self.refine_by = 2

    def _set_code_unit_attributes(self):
        # This is where quantities are created that represent the various
        # on-disk units.  These are the currently available quantities which
        # should be set, along with examples of how to set them to standard
        # values.
        # set to unitary
        #
        # self.length_unit = self.quan(1.0, "cm")
        # self.mass_unit = self.quan(1.0, "g")
        # self.time_unit = self.quan(1.0, "s")
        # self.time_unit = self.quan(1.0, "s")
        #
        # These can also be set:
        # self.velocity_unit = self.quan(1.0, "cm/s")
        # self.magnetic_unit = self.quan(1.0, "gauss")
        pass

    def _parse_parameter_file(self):
        # This needs to set up the following items.  Note that these are all
        # assumed to be in code units; domain_left_edge and domain_right_edge
        # will be converted to YTArray automatically at a later time.
        # This includes the cosmological parameters.
        #
        #   self.unique_identifier      <= unique identifier for the dataset
        #                                  being read (e.g., UUID or ST_CTIME)
        #   self.parameters             <= full of code-specific items of use

        file = nib.load("self")
        image_vals = file.get_fdata()
        # is where I store the numpy arrays?
        # or should this be the header values?
        self.parameters = image_vals

        self.header = file.get_header

        #   self.domain_left_edge       <= array of float64



        #   self.domain_right_edge      <= array of float64
        #   self.dimensionality         <= int

        self.dimensionality = image_vals.ndim

        #   self.domain_dimensions      <= array of int64

        self.domain_dimensions = image_vals.shape

        #   self.periodicity            <= three-element tuple of booleans 0

        self.periodicity = 0

        #   self.current_time           <= simulation time in code units 0

        self.current_time = 0

        #
        # We also set up cosmological information.  Set these to zero if
        # non-cosmological.
        #
        #   self.cosmological_simulation    <= int, 0 or 1
        #   self.current_redshift           <= float
        #   self.omega_lambda               <= float
        #   self.omega_matter               <= float
        #   self.hubble_constant            <= float

        self.cosmological_simulation =  0
        self.current_redshift  = 0
        self.omega_lambda = 0
        self.omega_matter = 0
        self.hubble_constant = 0

        pass


    @classmethod
    def _is_valid(self, *args, **kwargs):
        # unqiue MRI file format identifier
        try:
            if "nii" in args:
                file = nibabel.load("args")
                header = file.get_header
                array = file.get_fdata("args")
                if header == None:
                    return False
                if array =
                file.close()
                return True
            else:
                return False
        except:
            pass

