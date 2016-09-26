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

1. Install dependencies.
2. Fill in the `config.json` file.
3. Download the APK and run python3.5 patcher.py --json 1.5.0
    Note: The `keypass` and `dname` fields are only required to create a new keystore.  See [here](http://docs.oracle.com/javase/7/docs/technotes/tools/solaris/keytool.html#DName) for how to fill out the `dname` fields.

## Dependencies

- [Apktool](http://ibotpeaches.github.io/Apktool/)
- `keytool` and `jarsigner` from the [Java JDK](http://www.oracle.com/technetwork/java/javase/downloads/index.html)
- `zipalign` from the [Android SDK](http://developer.android.com/sdk/index.html#Other)
- [requests](http://python-requests.org/) and [requests-cache](https://github.com/reclosedev/requests-cache)

    Note: `requests` and `requests-cache` can be installed with:

        python3.5 -m pip install requests requests-cache
