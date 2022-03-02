# Population-One-Localizer
Locally cache assets that are normally streamed in POPULATION: ONE. Resolves numerous issues related to asset streaming & saves bandwith.

# Installation
1. Install the latest version of Python 3
2. Install tqdm via pip (pip install tqdm)
3. Download the latest version of UnityAssetReplacer from https://github.com/Skyluker4/UnityAssetReplacer/releases
4. Extract UnityAssetReplacer to a folder named "UnityAssetReplacer-win-x64" next to the localizer

# Usage
**You must perform this process after every game update**
1. Copy `catalog.bundle` from `your_pop_1_install_folder/PopulationONE_Data/StreamingAssets/aa` to the directory you extracted the localizer
2. Run `extract_bundle`. You should now have an `extract` folder with a `catalog` file inside. If this file is missing, you probably didn't copy `catalog.bundle` to the right place
3. Open `pop1_localizer.py` in a text editor, ensure that `build_number` is set to whatever is currently listed below
    - LIVE (non-playtest): 25402
    - Playtest:
4. Run `pop1_localizer.py`, wait for the download to complete (this is about 15GB worth of assets, so it may take some time)
5. Copy all of the `.bundle` files from the newly created `assets` folder to `your_pop_1_install_folder/PopulationONE_Data/StreamingAssets/aa/StandaloneWindows64`
6. Run `repack_bundle`
7. Copy `catalog.bundle` from the newly created `output` folder to `your_pop_1_install_folder/PopulationONE_Data/StreamingAssets/aa` and overwrite the existing file
