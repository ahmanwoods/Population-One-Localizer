import json
import os
from multiprocessing import Pool
from urllib.request import urlretrieve
from tqdm import tqdm

max_download_threads = 6
build_number = 25402

def get_urls():
    with open('extract\catalog') as catalog_file:
        urls = []
        catalog_json = json.load(catalog_file)
        for x in range(len(catalog_json['m_InternalIds'])):
            if "{BigBoxVR.UnityContentDeliveryManager.RemoteLoadPath}" in catalog_json['m_InternalIds'][x]:
                urls.append(("https://appcdn.bigboxvr.com/prod/Build" + str(build_number) + "/StandaloneWindows64/" + catalog_json['m_InternalIds'][x][54:], "assets/" + catalog_json['m_InternalIds'][x][54:]))
        return urls

def create_catalog():
    if not os.path.exists('replacement'):
        os.makedirs('replacement')

    with open('extract\catalog') as catalog_file:
        catalog_json = json.load(catalog_file)
        for x in range(len(catalog_json['m_InternalIds'])):
            if "{BigBoxVR.UnityContentDeliveryManager.RemoteLoadPath}" in catalog_json['m_InternalIds'][x]:
                catalog_json['m_InternalIds'][x] = catalog_json['m_InternalIds'][x].replace("{BigBoxVR.UnityContentDeliveryManager.RemoteLoadPath}\\", "{UnityEngine.AddressableAssets.Addressables.RuntimePath}\\StandaloneWindows64\\")
    
    with open('replacement\catalog', 'w') as output_json:
        json.dump(catalog_json, output_json)

def urlretrieve_unpack(args):
    return urlretrieve(*args)

if __name__ == '__main__':
    if not os.path.exists('assets'):
        os.makedirs('assets')

    urls = get_urls()
    create_catalog()
    with Pool(max_download_threads) as pool:
        tuple(tqdm(pool.imap(urlretrieve_unpack, urls), total=len(urls)))