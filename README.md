# iqdb-as-an-app
Core functionality of iqdb.org in a simple python app format

IQDB is a simple "Multi-service image search" as they call themselves, however
I think that their website is pretty boring-looking so I made an app that uses
their service and looks (in my opinion) still simple but better, with some quality
of life things like togglable 'always on top' and support for .webp files

anyways to use it you just need to download and run the iqdb.py
but you will need some libraries which are provided in the requirements.txt file
with versions I tested the app on (newer versions should work fine)
to install all libraries just download the requirements.txt go to it's directory and run
``
pip install -r requirements.txt
``
also __python 3.12__ recommended

**NEWEST UPDATE:** at the top of iqdb.py there is now variable set to "path_to_your_browser",
you can set it to your browser path if you want to use other than default browser **e.g.**
```py
browser_path = "C:/Program Files/Mozilla Firefox/firefox.exe"
```

If you have any questions/issues lmk in the issues tab or wherever :3
