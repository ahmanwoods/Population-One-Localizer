if not exist "output\" mkdir output

"UnityAssetReplacer-win-x64\UnityAssetReplacer.exe" -b "catalog.bundle" -i "replacement" -m m_Script -o "output\catalog.bundle"