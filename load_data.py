import yt
import nifti_frontend.api

ds = yt.load("nifti_frontend/mprage_skullstripped.nii.gz")

intensity = ds.r[:]["scan", "intensity"]
print(intensity)
