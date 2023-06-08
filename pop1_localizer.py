import json
import os
import shutil
from multiprocessing import Pool
from urllib.request import urlretrieve, urlopen

# ------------ CONFIGURATION-------------------------
# prod for live, dev for playtest
build_env = "prod"
# If this is set to 'auto', the program will attempt to extract the version from the github readme.
build_number = "auto"
max_download_threads = 6

# If you manually copied the json file to pop1_localisers folder, set the following to 'False'.
auto_fetch_json_file = True
# Set these to False to disable automatic installation of the respective files
auto_install_bundle_files = True
auto_install_replacement_json = True
# This can be either 'copy' or 'move'
install_method = "copy"
# Keep the original JSON File as original_name.json.bak
keep_original_json_backup = False
# --------- DEBUG -----------------------------------
skip_download = False
disable_tqdm = True
display_readme = False
# ----------------------------------------------------


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print("script_dir:", script_dir)
    if auto_fetch_json_file:
        # Get Rid of existing Json files in Script Dir
        json_files = [f for f in os.listdir(script_dir) if f.endswith(".json")]
        for file in json_files:
            if keep_original_json_backup:
                rename_add_extension_bak(file)
            else:
                os.remove(file)
        # Copy Over The newest JSON File
        original_json_file_path = get_latest_json_file_path()
        json_filename = os.path.basename(original_json_file_path)
        destination = os.path.join(script_dir, json_filename)
        install_file(original_json_file_path, destination, override="copy")
        print("Copied over", json_filename)

    if build_number == "auto":
        update_build_number()

    #### actually do stuff #####
    asset_path = os.path.join(script_dir, "assets")
    if not os.path.exists(asset_path):
        os.makedirs(asset_path)
    urls = get_urls()
    output_json_path = create_replacement_json()
    print("Downloading Files.")
    if not skip_download:
        with Pool(max_download_threads) as pool:
            progressbar(pool.imap(urlretrieve_unpack, urls), total=len(urls))
    #############################

    if auto_install_bundle_files:
        install_bundle_files()
    if auto_install_replacement_json:
        install_replacement_json(output_json_path)
    print("Done!")


def get_urls():
    file = get_local_json_file_path()

    with open(file) as catalog_file:
        url_list = []
        catalog_json = json.load(catalog_file)
        for x in range(len(catalog_json["m_InternalIds"])):
            if (
                "{BigBoxVR.UnityContentDeliveryManager.RemoteLoadPath}"
                in catalog_json["m_InternalIds"][x]
            ):
                urlstring = (
                    "https://appcdn.bigboxvr.com/PopOne/Assets/"
                    + build_number
                    + "/"
                    + build_env
                    + "/StandaloneWindows64/"
                    + catalog_json["m_InternalIds"][x][54:],
                    "assets/" + catalog_json["m_InternalIds"][x][54:],
                )
                url_list.append(urlstring)
        return url_list


def create_replacement_json():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    replacement_json_dir = os.path.join(script_dir, "replacement_json")
    json_source_file = get_local_json_file_path()
    json_file_name = os.path.basename(json_source_file)
    replacement_json_file = os.path.join(replacement_json_dir, json_file_name)

    if not os.path.exists(replacement_json_dir):
        os.makedirs(replacement_json_dir)

    with open(json_source_file) as catalog_file:
        catalog_json = json.load(catalog_file)
        for x in range(len(catalog_json["m_InternalIds"])):
            if (
                "{BigBoxVR.UnityContentDeliveryManager.RemoteLoadPath}"
                in catalog_json["m_InternalIds"][x]
            ):
                catalog_json["m_InternalIds"][x] = catalog_json[
                    "m_InternalIds"
                ][x].replace(
                    "{BigBoxVR.UnityContentDeliveryManager.RemoteLoadPath}\\",
                    "{UnityEngine.AddressableAssets.Addressables.RuntimePath}\\StandaloneWindows64\\",
                )

    with open(replacement_json_file, "w") as output_json:
        json.dump(catalog_json, output_json)
    return replacement_json_file


def urlretrieve_unpack(args):
    try:
        return urlretrieve(*args)
    except Exception as e:
        print(e)
        return True


def progressbar(iterable, total):
    if not disable_tqdm:
        try:
            from tqdm import tqdm

            tuple(tqdm(iterable, total=total))
            return
        except ImportError:
            print("Please run 'pip install tqdm' for a fancy progress bar.")
    import time

    update_interval = 2.5
    start = time.time()
    last_update = start - update_interval + 1.0
    for i, _ in enumerate(iterable):
        if time.time() > last_update + update_interval:
            last_update = time.time()
            elapsed_time = time.time() - start
            remaining_time = elapsed_time * (total / i) - elapsed_time
            completed = time.asctime(
                time.localtime(time.time() + remaining_time)
            ).split()[-2]
            print(
                f"{i}/{total} files.({round(i/total*100)}%) Elapsed: {int(elapsed_time)} s. "
                + f"ETA:~{completed}; {remaining_time:.1f}s to go"
            )


def get_latest_json_file_path():
    username = os.getlogin().lower()
    json_dir = f"C:/Users/{username}/AppData/LocalLow/BigBoxVR/Population_ ONE/com.unity.addressables"
    json_dir = json_dir.replace("/", "\\")
    print(json_dir)

    json_files = [f for f in os.listdir(json_dir) if f.endswith(".json")]

    json_files = [os.path.join(json_dir, file) for file in json_files]

    if not json_files:
        print(f"Couldnt find any JSON-Files in {json_dir}.")
        print("Launching once to the main menu should generate one.")
        print(
            "You can set 'auto_fetch_json_file' to 'False' and copy the file over yourself."
        )
        raise FileNotFoundError("Auto Fetching Latest JSON File failed")

    json_files.sort(key=os.path.getmtime)
    latest_file = json_files[-1]
    return latest_file


def install_file(source_file, destination_file, override=False):
    """Moves/copies the provided files according to the configuration"""
    chosen_install_method = override if override else install_method
    assert chosen_install_method in ["move", "copy"]
    assert os.path.exists(source_file)
    assert not os.path.exists(destination_file)
    if chosen_install_method == "copy":
        shutil.copy(source_file, destination_file)
    if chosen_install_method == "move":
        os.rename(source_file, destination_file)
    assert os.path.exists(destination_file)


def rename_add_extension_bak(target_file):
    renamed_path = target_file + ".bak"
    while os.path.exists(renamed_path):
        renamed_path += "x"
    os.rename(target_file, renamed_path)
    return renamed_path


def update_build_number():
    print("Trying to retrieve the current Build Number...")
    url = "https://raw.githubusercontent.com/ahmanwoods/Population-One-Localizer/main/README.md"
    look_for_this = "LIVE (non-playtest):"

    # make request
    response = urlopen(url)
    content = response.read().decode("utf8")
    if display_readme:
        print(content)
    lines = content.split("\n")

    # extract build number
    for line in lines:
        if look_for_this in line:
            version = line.split()[-1]
            global build_number
            build_number = version
            print("Curent Build Number in Github Readme is", version)
            return version

    print("Unable to fetch the Current Version from the Github Readme.")
    print(
        "You will have to manually set it to proceed. Go to 'current_version', and replace 'auto' with the correct string."
    )
    raise Exception("Cannot extract Version from " + url)


def get_population_install_location():
    libraryfolders = (
        "C:\\Program Files (x86)\\Steam\\steamapps\\libraryfolders.vdf"
    )
    STEAM_POP1_APPID = "691260"
    if os.path.isfile(libraryfolders):
        with open(libraryfolders) as f:
            lines = f.readlines()

            found_pop_1 = False
            for line in reversed(lines):
                if STEAM_POP1_APPID in line:
                    found_pop_1 = True
                    print(
                        "Successfully found Population ONE appid, backtracking to find corresponding library..."
                    )
                if found_pop_1 and '"path"' in line:
                    librarypath = line.replace('"path"', "")
                    librarypath = librarypath.strip().replace('"', "")
                    to_pop1 = "steamapps\\common\\PopulationONE"
                    install_path = os.path.join(librarypath, to_pop1)
                    print("LibraryPath:", install_path)
                    if os.path.isdir(install_path):
                        return install_path
    print("Couldnt Find your Steam POPULATION:ONE Install Location..")
    print("Thus, the bundle files cannot be automatically installed.")
    print("You will have to copy them over manually.")
    print("FROM: all the '.bundle files in the newly created assets folder")
    print(
        "TO: your_pop_1_install_folder/PopulationONE_Data/StreamingAssets/aa/StandaloneWindows64"
    )
    raise ValueError("Couldnt Find the Steam POPULATION:ONE Libraryfolder")


def install_bundle_files():
    print("Determining Pop1 install location...")
    install_location = get_population_install_location()
    directory = "PopulationONE_Data/StreamingAssets/aa/StandaloneWindows64"
    directory = directory.replace("/", "\\")
    dest_dir = os.path.join(install_location, directory)
    print("Population One is installed at", install_location)
    print(".bundle Files will be moved to", dest_dir)

    print("Taking inventory of bundle files to be installed...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(script_dir, "assets")
    pairs = [
        (os.path.join(source_dir, f), os.path.join(dest_dir, f))
        for f in os.listdir(source_dir)
        if f.endswith(".bundle")
    ]

    def iterable_install_files(pairs):
        for source, destination in pairs:
            install_file(source, destination)
            yield destination

    print("Installing Bundle Files...")
    progressbar(iterable_install_files(pairs), total=len(pairs))
    print(f"Installed ({install_method})", len(pairs), ".bundle files.")


def install_replacement_json(output_json_path):
    print("Installing replacement JSON...")
    username = os.getlogin().lower()
    json_dir = f"C:/Users/{username}/AppData/LocalLow/BigBoxVR/Population_ ONE/com.unity.addressables"
    json_dir = json_dir.replace("/", "\\")
    json_filename = os.path.basename(output_json_path)
    destination_file = os.path.join(json_dir, json_filename)

    if os.path.exists(destination_file):
        if keep_original_json_backup:
            rename_add_extension_bak(destination_file)
        elif not keep_original_json_backup:
            os.remove(destination_file)
    install_file(output_json_path, destination_file)


def get_local_json_file_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_files = [f for f in os.listdir(".") if f.endswith(".json")]
    if len(json_files) != 1:
        raise ValueError("multiple json files in the current directory")
    json_source_file = os.path.join(script_dir, json_files[0])
    return json_source_file


if __name__ == "__main__":
    main()
