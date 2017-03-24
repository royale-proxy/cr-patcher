**Warning:** In April 2016, Supercell has started banning accounts for the use of third party software. We are unsure what, if any, checks are in place that might reveal the use of this tool, so continue at your own risk. See [here](http://supercell.com/en/safe-and-fair-play/) for more info.

# cr-patcher

This tool applies some patches to the APK of Clash Royale. With them, your game will connect with its official servers through a [cr-proxy](https://github.com/royale-proxy/cr-proxy) on your computer instead of directly. Thanks to that, you will be able to see every message that is sent to the server, and from server to your client, in an easily readable way.

## Running
#### Read the [installation](#installation) section before
Then, to start, you need an .apk of the game. You can download an official one for example [here](http://www.apkmirror.com/uploads/?q=clash-royale-supercell). Put it to this folder (the one where `patcher.py` is). The name should match the following format:

    <package>-<version>.apk
    
If you use the official APK, the package is `com.supercell.clashroyale`, so an example file name is `com.supercell.clashroyale-1.8.1.apk`

Run the script with:

    python3.5 patcher.py [--json] version-number

For example:

    python3.5 patcher.py 1.8.1

By default, `cr-patcher` will retrieve the keys, MD5s, and key and URL offsets from the [`cr-proxy` wiki](https://github.com/royale-proxy/cr-proxy/wiki).  To provide these values for a new or unknown APK version, enter them in `config.json` and use the `--json` flag. 

<details><summary>If you need to, enter them with this layout (click to expand)</summary><p>

```
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
```
</p></details>

## Config explained
* `debug` *(true/false)* - when it's true, you can use external tools to debug the app when it's running. If you only want to run the [proxy](https://github.com/royale-proxy/cr-proxy), you probably won't need this, but most likely you also won't have any reason to disable this.
* `package` - if you somehow changed the package in game files before, change it here also (remember to [change the name](#cr-patcher) of .apk). The main reason for changing it is to make it possible to install both the original Clash Royale and your modified version at the same time. And no, this tool doesn't change the package automatically.
* `key` - you shouldn't have any reason to change this. The default key guarantees that after patching the game will be able to connect to `cr-proxy`. If you change the key, it won't be. Leave this default unless you know what you're doing.
* `url` - the address of server which the game will connect to. The default one, `game.clashroyaleapp.com`, is 23 characters long. Yours also has to have 23 characters. If you have a domain, you can add a subdomain and redirect it to the proxy. The official server of Clash Royale is running on port 9339, so is the proxy. The game will always look for a server at this port, that's why there is no `port` field in this config. Also, don't try to add the port like `the.ip.here:1337`
* `keystore` - if the key used to sign the app changes, you won't be able to update it without uninstalling the previous version before. You can learn more about signing Android apps for example [here](https://developer.android.com/studio/publish/app-signing.html) Also note, the `keypass` and `dname` fields are only required to create a new keystore.  See [here](http://docs.oracle.com/javase/7/docs/technotes/tools/solaris/keytool.html#DName) for how to fill out the `dname` fields (if you want to, but that isn't important).
* `versions` - if you need to change something here - experiment, ask around, or wait for someone else to do it for you, when a new version is out 

## Installation

1. Install [dependencies](#dependencies).
2. Copy the `config.json.example` file to `config.json` (so you can do it again when you break something) and fill it in. The changes that you *have* to made are:
* in `paths`, set `apktool` to the path of your Apktool wrapper script. If you exactly followed the instructions on their website, on Windows, the path is `C:\\Windows\\apktool.bat` while on Linux and Mac `/usr/local/bin/apktool`
* in `paths`, set `zipalign` to the path of that program (look at [dependencies](#dependencies))
    **Note:** On Windows, use either `/` to separate folders in path, or use double `\` -> `\\`, because of how json works.
3. You may want to change a [few more things](#config-expained) in the config
4. Read the [running](#running) section

## Dependencies

- Apktool - [home page](http://ibotpeaches.github.io/Apktool/) - [download & install instructions](http://ibotpeaches.github.io/Apktool/install)
- `keytool` and `jarsigner` from the [Java JDK](http://www.oracle.com/technetwork/java/javase/downloads/index.html), on Windows most likely can be found in `C:\Program Files\Java\<version>\bin\`
- `zipalign` from the [Android SDK](http://developer.android.com/sdk/index.html#Other)
    
    If you haven't already, install Android Studio, open it, download SDK for any version of Android (the one that will be chosen by default, lastest stable, should be fine). Then, you can find `zipalign` in `<sdk-folder>/build-tools/<version>/zipalign(.exe on Windows)`. 
    
    For example, on Linux, I found it in `~/Android/Sdk/build-tools/25.0.2/zipalign`
    
    If you wouldn't like to download the whole Android Studio, you can scroll the download page down to *Get just the command line tools*. Download the version for your OS, unzip it, run `sdkmanager(.exe)` (this program has a gui), download one version of SDK, just like you would do in Android Studio. Rest works like above ^  
- [requests](http://python-requests.org/) and [requests-cache](https://github.com/reclosedev/requests-cache)

    Note: `requests` and `requests-cache` can be installed with:
    
        python3.5 -m pip install requests requests-cache

    To install it this way, you need `pip`. Check if you have it with `pip --version`, if you don't, on Ubuntu you can get it with 
    
        apt-get -y install python-pip
