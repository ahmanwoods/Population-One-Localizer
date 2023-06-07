import json
import os
from multiprocessing import Pool
from urllib.request import urlretrieve
from tqdm import tqdm

max_download_threads = 6
#prod for live, dev for playtest
build_env = "prod"
build_number = "v278"

def get_urls():
    json_files = [f for f in os.listdir('.') if f.endswith('.json')]
    if len(json_files) != 1:
        raise ValueError('multiple json files in the current directory')
    global file
    file = json_files[0]
    with open(file) as catalog_file:
        urls = []
        catalog_json = json.load(catalog_file)
        for x in range(len(catalog_json['m_InternalIds'])):
            if "{BigBoxVR.UnityContentDeliveryManager.RemoteLoadPath}" in catalog_json['m_InternalIds'][x]:
                urls.append(("https://appcdn.bigboxvr.com/PopOne/Assets/" + build_number + "/" + build_env + "/StandaloneWindows64/" + catalog_json['m_InternalIds'][x][54:], "assets/" + catalog_json['m_InternalIds'][x][54:]))
        return urls

def create_catalog():
    if not os.path.exists('replacement_json'):
        os.makedirs('replacement_json')

    with open(file) as catalog_file:
        catalog_json = json.load(catalog_file)
        for x in range(len(catalog_json['m_InternalIds'])):
            if "{BigBoxVR.UnityContentDeliveryManager.RemoteLoadPath}" in catalog_json['m_InternalIds'][x]:
                catalog_json['m_InternalIds'][x] = catalog_json['m_InternalIds'][x].replace("{BigBoxVR.UnityContentDeliveryManager.RemoteLoadPath}\\", "{UnityEngine.AddressableAssets.Addressables.RuntimePath}\\StandaloneWindows64\\")
    
    with open('replacement_json\\' + file, 'w') as output_json:
        json.dump(catalog_json, output_json)

def urlretrieve_unpack(args):
    try:
        return urlretrieve(*args)
    except Exception as e:
        print(e)
        return True

if __name__ == '__main__':
    if not os.path.exists('assets'):
        os.makedirs('assets')

    urls = get_urls()
    create_catalog()
    with Pool(max_download_threads) as pool:
        tuple(tqdm(pool.imap(urlretrieve_unpack, urls), total=len(urls)))
