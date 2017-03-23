**Warning:** Your account may be banned for using these tools

# cr-patcher

_Patches and signs the Clash Royale APK_

Run with:

    python3.5 patcher.py [--json] version-number

For example:

    python3.5 patcher.py 1.5.0

By default, `cr-patcher` will retrieve the keys, MD5s, and key and URL offsets from the [`cr-proxy` wiki](https://github.com/royale-proxy/cr-proxy/wiki).  To provide these values for a new or unknown APK version, enter them in `config.json` and use the `--json` flag.  Enter them with the following layout:

    "versions": {
      "8.212.9": {
        "key": "469b704e7f6009ba8fc72e9b5c864c8e9285a755c5190f03f5c74852f6d9f419",
        "arm": {
          "md5": "769e2e9e1258b75d15cb7e04b2e49de3",
          "key-offset": "4280344",
          "url-offset": "3534513"
        },
        "x86": {
          "md5": "29ca23e48a5e419e83f2a7988c842d3e",
          "key-offset": "6189080",
          "url-offset": "4768816"
        }
      }
    }

## Installation

1. Install [dependencies](#dependencies).
2. Fill in the `config.json` file. The changes that you *have* to made are:
* in `paths`, set `apktool` to the path of your Apktool wrapper script. If you exactly followed the instructions on their website, on Windows, the path is `C:\Windows\apktool.bat` while on Linux and Mac `/usr/local/bin/apktool`
* in `paths`, set `zipalign` to the path of this program (look in the *Dependencies* section)
3. Download the APK and run python3.5 patcher.py --json 1.5.0
    Note: The `keypass` and `dname` fields are only required to create a new keystore.  See [here](http://docs.oracle.com/javase/7/docs/technotes/tools/solaris/keytool.html#DName) for how to fill out the `dname` fields.

## Dependencies

- Apktool - [home page](http://ibotpeaches.github.io/Apktool/) - [download & install instructions](http://ibotpeaches.github.io/Apktool/install)
- `keytool` and `jarsigner` from the [Java JDK](http://www.oracle.com/technetwork/java/javase/downloads/index.html)
- `zipalign` from the [Android SDK](http://developer.android.com/sdk/index.html#Other)
    
    If you haven't already, install Android Studio, open it, download SDK for any version of Android (the one that will be chosen by default, lastest stable, should be fine). Then, you can find `zipalign` in `<sdk-folder>/build-tools/<version>/zipalign(.exe on Windows)`. 
    
    For example, on Linux, I found it in `~/Android/Sdk/build-tools/25.0.2/zipalign`
    
    If you wouldn't like to download the whole Android Studio, you can scroll the download page down to *Get just the command line tools*. Download the version for your OS, unzip it, run `sdkmanager(.exe)` (this program has a gui), download one version of SDK, just like you would do in Android Studio. Rest works like above ^  
- [requests](http://python-requests.org/) and [requests-cache](https://github.com/reclosedev/requests-cache)

    Note: `requests` and `requests-cache` can be installed with:
    
        python3.5 -m pip install requests requests-cache

    To install it this way, you need `pip`. Check if you have it with `pip --version`, if you don't, on Ubuntu you can get it with 
    
        apt-get -y install python-pip
