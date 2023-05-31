# Population One Localizer
Locally cache assets that are normally streamed in POPULATION: ONE. Resolves numerous issues related to asset streaming & saves bandwith.

# Installation
1. Install the latest version of Python 3
2. Install tqdm via pip (pip install tqdm)

# Usage
**You must perform this process after every game update**
1. Boot your game up and go to the main menu at least once
2. Copy the `.json` file from `C:\Users\yourusername\AppData\LocalLow\BigBoxVR\Population_ ONE\com.unity.addressables` to the directory you extracted the localizer
3. Open `pop1_localizer.py` in a text editor, ensure that `build_number` is set to whatever is currently listed below
    - LIVE (non-playtest): v266
4. Run `pop1_localizer.py`, wait for the download to complete (this is about 35GB worth of assets, so it will take some time)
5. Copy all of the `.bundle` files from the newly created `assets` folder to `your_pop_1_install_folder/PopulationONE_Data/StreamingAssets/aa/StandaloneWindows64`
7. Copy the `.json` file from the newly created `replacement_json` folder to `C:\Users\yourusername\AppData\LocalLow\BigBoxVR\Population_ ONE\com.unity.addressables` and overwrite the existing file
