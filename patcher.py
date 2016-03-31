from collections import OrderedDict
from xml.etree import ElementTree
import argparse
import os
import sys
import json
import requests
import requests_cache
import subprocess
import shutil

parser = argparse.ArgumentParser()
parser.add_argument('version', help='client version')
parser.add_argument('--json', help='use config.json for version info', action='store_true')
args = parser.parse_args()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RELEASE_NAME = 'com.supercell.clashofclans-{}'.format(args.version)
DECODED_DIR = os.path.join(BASE_DIR, RELEASE_NAME)
MANIFEST_PATH = os.path.join(DECODED_DIR, 'AndroidManifest.xml')
LIBG_ARM = os.path.join(DECODED_DIR, 'lib', 'armeabi-v7a', 'libg.so')
LIBG_X86 = os.path.join(DECODED_DIR, 'lib', 'x86', 'libg.so')
BUILD_DIR = os.path.join(DECODED_DIR, 'build')
APK_FILENAME = '{}.apk'.format(RELEASE_NAME)
APK_PATH = os.path.join(BASE_DIR, APK_FILENAME)
BACKUP_PATH = os.path.join(BASE_DIR, '{}-orig.apk'.format(RELEASE_NAME))
UNSIGNED_PATH = os.path.join(BUILD_DIR, '{}-unsigned.apk'.format(RELEASE_NAME))
UNALIGNED_PATH = os.path.join(BUILD_DIR, '{}-unaligned.apk'.format(RELEASE_NAME))
PATCHED_PATH = os.path.join(BASE_DIR, APK_FILENAME)
KEYSTORE_PATH = os.path.join(BASE_DIR, 'client.keystore')

def ask(question):
    while True:
        response = input('{} (y/n): '.format(question))
        if response.lower() in ['yes', 'y']:
            return True
        elif response.lower() in ['no', 'n']:
            return False

print('Getting config ...')

if not os.path.isfile(os.path.join(BASE_DIR, 'config.json')):
    print('ERROR: config.json does not exist.', file=sys.stderr)
    sys.exit(1)

try:
    with open(os.path.join(BASE_DIR, 'config.json')) as fp:
        config = json.load(fp, object_pairs_hook=OrderedDict)
except json.decoder.JSONDecodeError as e:
    print('ERROR: Failed to decode config.json.', file=sys.stderr)
    sys.exit(1)
else:
    if 'debug' not in config:
        config['debug'] = False

print('Checking environment ...')

if not os.path.isfile(APK_PATH):
    print('ERROR: {} does not exist.'.format(APK_FILENAME), file=sys.stderr)
    sys.exit(1)

if 'package' not in config or not config['package']:
    print('ERROR: New package ID missing from config.json.', file=sys.stderr)
    sys.exit(1)
if 'key' not in config or not config['key']:
    print('ERROR: New key missing from config.json.', file=sys.stderr)
    sys.exit(1)
else:
    try:
        bytes.fromhex(config['key'])
    except (TypeError, ValueError) as e:
        print('ERROR: Failed to decode key.', file=sys.stderr)
        sys.exit(1)
    else:
        if len(bytes.fromhex(config['key'])) != 32:
            print('ERROR: New key must be 32 bytes.', file=sys.stderr)
            sys.exit(1)
if 'url' not in config or not config['url']:
    print('ERROR: New URL missing from config.json.', file=sys.stderr)
    sys.exit(1)
elif len(config['url']) != 22:
    print('ERROR: New URL must be exactly 22 characters.', file=sys.stderr)
    sys.exit(1)

if 'keystore' not in config or not config['keystore']:
    print('ERROR: Keystore info missing from config.json.', file=sys.stderr)
    sys.exit(1)
if 'storepass' not in config['keystore'] or not config['keystore']['storepass']:
    print('ERROR: Keystore storepass missing from config.json.', file=sys.stderr)
    sys.exit(1)
if 'key' not in config['keystore'] or not config['keystore']['key']:
    print('ERROR: Signing key info missing from config.json.', file=sys.stderr)
    sys.exit(1)
if 'alias' not in config['keystore']['key'] or not config['keystore']['key']['alias']:
    print('ERROR: Signing key alias missing from config.json.', file=sys.stderr)
    sys.exit(1)

if not os.path.isfile(KEYSTORE_PATH):
    if ask('client.keystore does not exist. Would you like to create it?'):
        if 'keypass' not in config['keystore']['key'] or not config['keystore']['key']['keypass']:
            print('ERROR: Signing key keypass missing from config.json.', file=sys.stderr)
            sys.exit(1)
        if 'dname' not in config['keystore']['key'] or not config['keystore']['key']['dname']:
            print('ERROR: Signing key dname info missing from config.json.', file=sys.stderr)
            sys.exit(1)
        if 'cn' not in config['keystore']['key']['dname'] or not config['keystore']['key']['dname']['cn']:
            print('ERROR: Signing key dname cn missing from config.json.', file=sys.stderr)
            sys.exit(1)
        if 'ou' not in config['keystore']['key']['dname'] or not config['keystore']['key']['dname']['ou']:
            print('ERROR: Signing key dname ou missing from config.json.', file=sys.stderr)
            sys.exit(1)
        if 'o' not in config['keystore']['key']['dname'] or not config['keystore']['key']['dname']['o']:
            print('ERROR: Signing key dname o missing from config.json.', file=sys.stderr)
            sys.exit(1)
        if 'l' not in config['keystore']['key']['dname'] or not config['keystore']['key']['dname']['l']:
            print('ERROR: Signing key dname l missing from config.json.', file=sys.stderr)
            sys.exit(1)
        if 's' not in config['keystore']['key']['dname'] or not config['keystore']['key']['dname']['s']:
            print('ERROR: Signing key dname s missing from config.json.', file=sys.stderr)
            sys.exit(1)
        if 'c' not in config['keystore']['key']['dname'] or not config['keystore']['key']['dname']['c']:
            print('ERROR: Signing key dname c missing from config.json.', file=sys.stderr)
            sys.exit(1)

        dname = ', '.join('{}={}'.format(key, val.translate(str.maketrans({',': '\,'}))) for key, val in config['keystore']['key']['dname'].items())
        result = subprocess.run([config['paths']['keytool'], '-genkey', '-keystore', KEYSTORE_PATH, '-storepass', config['keystore']['storepass'], '-alias', config['keystore']['key']['alias'], '-keypass', config['keystore']['key']['keypass'], '-dname', dname, '-keyalg', 'RSA', '-keysize', '2048', '-validity', '10000'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            result.check_returncode()
        except subprocess.CalledProcessError as e:
            print('ERROR: Failed to create keystore.', file=sys.stderr)
            sys.exit(1)
    else:
        print('ERROR: client.keystore is missing.', file=sys.stderr)
        sys.exit(1)

result = subprocess.run([config['paths']['keytool'], '-list', '-keystore', KEYSTORE_PATH, '-storepass', config['keystore']['storepass'], '-alias', config['keystore']['key']['alias']], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
try:
    result.check_returncode()
except subprocess.CalledProcessError as e:
    print('ERROR: Failed to load key from keystore.', file=sys.stderr)
    sys.exit(1)
else:
    if result.stdout.split('\n')[0].strip(', ').split(', ')[-1] != 'PrivateKeyEntry':
        print('ERROR: Key alias must refer to a private key.', file=sys.stderr)
        sys.exit(1)

if 'paths' not in config:
    print('ERROR: Paths are missing from config.json.', file=sys.stderr)
    sys.exit(1)
dependencies = ['apktool', 'md5sum', 'dd', 'keytool', 'jarsigner', 'zipalign']
for dependency in dependencies:
    if dependency not in config['paths'] or not config['paths'][dependency]:
        print('ERROR: {} path is missing from config.json.'.format(dependency), file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(config['paths'][dependency]):
        print('ERROR: {} path does not exist.'.format(dependency), file=sys.stderr)
        sys.exit(1)
    if not os.access(config['paths'][dependency], os.X_OK):
        print('ERROR: {} path is not executable.'.format(dependency), file=sys.stderr)
        sys.exit(1)

print('Getting version info ...')

if args.json:
    if args.version in config['versions']:
        info = config['versions'][args.version]
    else:
        print('ERROR: Version info is missing from config.json.', file=sys.stderr)
        sys.exit(1)
else:
    class VersionError(Exception):
        def __init__(self, value):
            self.value = value
        def __str__(self):
            return repr(self.value)

    def retrieve_version_info():
        pages = OrderedDict([
            ('keys', {
                'url': 'https://github.com/clugh/coc-proxy/wiki/Keys.md',
                'fields' : ['version', 'key']
            }),
            ('key-offsets', {
                'url': 'https://github.com/clugh/coc-proxy/wiki/Key-Offsets.md',
                'fields' : ['version', 'arch', 'md5', 'offset']
            }),
            ('url-offsets', {
                'url': 'https://github.com/clugh/coc-proxy/wiki/URL-Offsets.md',
                'fields' : ['version', 'arch', 'md5', 'offset']
            })
        ])

        requests_cache.install_cache('cache')

        def parse_table(url):
            return [[cell.strip().strip('`') for cell in line.strip('|').split('|')] for line in requests.get(url).text.split('\n') if args.version in line]

        data = {k: [OrderedDict(zip(v['fields'], line)) for line in parse_table(v['url'])] for k,v in pages.items()}
        for k,v in pages.items():
            if not data[k]:
                raise VersionError('{} not in {}.'.format(args.version, k))
        info = OrderedDict()
        info['key'] = data['keys'][0]['key']
        for line in data['key-offsets']:
            info[line['arch']] = OrderedDict()
            info[line['arch']]['md5'] = line['md5']
            info[line['arch']]['key-offset'] = line['offset']
        for line in data['url-offsets']:
            if line['arch'] not in info:
                raise VersionError('{} not in key-offsets.'.format(line['arch']))
            if line['md5'] != info[line['arch']]['md5']:
                raise VersionError('MD5s for {} do not match.'.format(line['arch']))
            info[line['arch']]['url-offset'] = line['offset']
        return info

    try:
        info = retrieve_version_info()
    except VersionError as e:
        if config['debug']:
            print('Version missing from cache. Clearing and retrieving again ...')
        requests_cache.clear()
        try:
            info = retrieve_version_info()
        except VersionError as e:
            if config['debug']:
                print('ERROR: Version is missing from wiki ({}).'.format(str(e).rstrip('.')), file=sys.stderr)
            else:
                print('ERROR: Version is missing from wiki.', file=sys.stderr)
            sys.exit(1)
    if 'versions' not in config:
        config['versions'] = {}
    config['versions'][args.version] = info
    with open('config.json', 'w') as fp:
        json.dump(config, fp, indent=2)
print(json.dumps(info, indent=2))

print('Decoding APK ...')

result = subprocess.run([config['paths']['apktool'], 'd', '-o', DECODED_DIR, '-f', APK_PATH], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
try:
    result.check_returncode()
except subprocess.CalledProcessError as e:
    if config['debug']:
        print('ERROR: Failed to decode {} ({}).'.format(APK_FILENAME, result.stderr.strip().rstrip('.').replace('{}/'.format(BASE_DIR), '')), file=sys.stderr)
    else:
        print('ERROR: Failed to decode {}.'.format(APK_FILENAME), file=sys.stderr)
    sys.exit(1)

print('Checking AndroidManifest.xml ...')

if not os.path.isfile(MANIFEST_PATH):
    print('ERROR: AndroidManifest.xml is missing.', file=sys.stderr)
    sys.exit(1)

print('Checking package ID ...')

ElementTree.register_namespace('android', 'http://schemas.android.com/apk/res/android')
try:
    tree = ElementTree.parse('{}'.format(MANIFEST_PATH))
except ElementTree.ParseError as e:
    print('ERROR: Failed to parse AndroidManifest.xml.', file=sys.stderr)
    sys.exit(1)

root = tree.getroot()
if root.get('package') != 'com.supercell.clashofclans':
    print('ERROR: Package is incorrect.', file=sys.stderr)
    sys.exit(1)

print('Patching package ID ...')

root.set('package', config['package'])
tree.write(MANIFEST_PATH, encoding='utf-8', xml_declaration=True)

print('Verifying package ID ...')

try:
    tree = ElementTree.parse('{}'.format(MANIFEST_PATH))
except ElementTree.ParseError as e:
    print('ERROR: Failed to parse AndroidManifest.xml.', file=sys.stderr)
    sys.exit(1)

root = tree.getroot()
if root.get('package') != config['package']:
    print('ERROR: Package is incorrect.', file=sys.stderr)
    sys.exit(1)

print('Checking libg.so ...')

if not os.path.isfile(LIBG_X86):
    print('ERROR: arm libg.so is missing.', file=sys.stderr)
    sys.exit(1)

if not os.path.isfile(LIBG_X86):
    print('ERROR: x86 libg.so is missing.', file=sys.stderr)
    sys.exit(1)

result = subprocess.run([config['paths']['md5sum'], LIBG_ARM], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
try:
    result.check_returncode()
except subprocess.CalledProcessError as e:
    print('ERROR: Failed to get arm libg.so MD5.', file=sys.stderr)
    print(result.stderr)
    print(result.stdout)
    sys.exit(1)
else:
    if result.stdout.split()[0].lstrip('\\') != info['arm']['md5']:
        print('ERROR: arm libg.so MD5 is incorrect.', file=sys.stderr)
        sys.exit(1)

result = subprocess.run([config['paths']['md5sum'], LIBG_X86], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
try:
    result.check_returncode()
except subprocess.CalledProcessError as e:
    print('ERROR: Failed to get arm libg.so MD5.', file=sys.stderr)
    sys.exit(1)
else:
    if result.stdout.split()[0].lstrip('\\') != info['x86']['md5']:
        print('ERROR: x86 libg.so MD5 is incorrect.', file=sys.stderr)
        sys.exit(1)

print('Checking keys ...')

result = subprocess.run([config['paths']['dd'], 'if={}'.format(LIBG_ARM), 'skip={}'.format(info['arm']['key-offset']), 'bs=1', 'count=32'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
try:
    result.check_returncode()
except subprocess.CalledProcessError as e:
    print('ERROR: Failed to get current arm libg.so key.', file=sys.stderr)
    sys.exit(1)
else:
    if result.stdout.hex() != info['key']:
        print('ERROR: Current arm libg.so key is incorrect.', file=sys.stderr)
        sys.exit(1)

result = subprocess.run([config['paths']['dd'], 'if={}'.format(LIBG_X86), 'skip={}'.format(info['x86']['key-offset']), 'bs=1', 'count=32'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
try:
    result.check_returncode()
except subprocess.CalledProcessError as e:
    print('ERROR: Failed to get current x86 libg.so key.', file=sys.stderr)
    sys.exit(1)
else:
    if result.stdout.hex() != info['key']:
        print('ERROR: Current x86 libg.so key is incorrect.', file=sys.stderr)
        sys.exit(1)

print('Checking URLs ...')

result = subprocess.run([config['paths']['dd'], 'if={}'.format(LIBG_ARM), 'skip={}'.format(info['arm']['url-offset']), 'bs=1', 'count=22'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
try:
    result.check_returncode()
except subprocess.CalledProcessError as e:
    print('ERROR: Failed to get current arm libg.so URL.', file=sys.stderr)
    sys.exit(1)
else:
    try:
        result.stdout.decode()
    except UnicodeDecodeError as e:
        print('ERROR: Failed to get current arm libg.so URL.', file=sys.stderr)
        sys.exit(1)
    else:
        if result.stdout.decode() != 'gamea.clashofclans.com':
            print('ERROR: Current arm libg.so URL is incorrect.', file=sys.stderr)
            sys.exit(1)

result = subprocess.run([config['paths']['dd'], 'if={}'.format(LIBG_X86), 'skip={}'.format(info['x86']['url-offset']), 'bs=1', 'count=22'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
try:
    result.check_returncode()
except subprocess.CalledProcessError as e:
    print('ERROR: Failed to get current x86 libg.so URL.', file=sys.stderr)
    sys.exit(1)
else:
    try:
        result.stdout.decode()
    except UnicodeDecodeError as e:
        print('ERROR: Failed to get current x86 libg.so URL.', file=sys.stderr)
        sys.exit(1)
    else:
        if result.stdout.decode() != 'gamea.clashofclans.com':
            print('ERROR: Current x86 libg.so URL is incorrect.', file=sys.stderr)
            sys.exit(1)

print('Patching keys ...')

result = subprocess.run([config['paths']['dd'], 'of={}'.format(LIBG_ARM), 'seek={}'.format(info['arm']['key-offset']), 'bs=1', 'count=32', 'conv=notrunc'], input=bytes.fromhex(config['key']), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
try:
    result.check_returncode()
except subprocess.CalledProcessError as e:
    print('ERROR: Failed to patch arm libg.so key.', file=sys.stderr)
    sys.exit(1)

result = subprocess.run([config['paths']['dd'], 'of={}'.format(LIBG_X86), 'seek={}'.format(info['x86']['key-offset']), 'bs=1', 'count=32', 'conv=notrunc'], input=bytes.fromhex(config['key']), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
try:
    result.check_returncode()
except subprocess.CalledProcessError as e:
    print('ERROR: Failed to patch x86 libg.so key.', file=sys.stderr)
    sys.exit(1)

print('Patching URLs ...')

result = subprocess.run([config['paths']['dd'], 'of={}'.format(LIBG_ARM), 'seek={}'.format(info['arm']['url-offset']), 'bs=1', 'count=22', 'conv=notrunc'], input=config['url'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
try:
    result.check_returncode()
except subprocess.CalledProcessError as e:
    print('ERROR: Failed to patch arm libg.so URL.', file=sys.stderr)
    sys.exit(1)

result = subprocess.run([config['paths']['dd'], 'of={}'.format(LIBG_X86), 'seek={}'.format(info['x86']['url-offset']), 'bs=1', 'count=22', 'conv=notrunc'], input=config['url'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
try:
    result.check_returncode()
except subprocess.CalledProcessError as e:
    print('ERROR: Failed to patch x86 libg.so URL.', file=sys.stderr)
    sys.exit(1)

print('Verifying keys ...')

result = subprocess.run([config['paths']['dd'], 'if={}'.format(LIBG_ARM), 'skip={}'.format(info['arm']['key-offset']), 'bs=1', 'count=32'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
try:
    result.check_returncode()
except subprocess.CalledProcessError as e:
    print('ERROR: Failed to get new arm libg.so key.', file=sys.stderr)
    sys.exit(1)
else:
    if result.stdout.hex() != config['key']:
        print('ERROR: New arm libg.so key is incorrect.', file=sys.stderr)
        sys.exit(1)

result = subprocess.run([config['paths']['dd'], 'if={}'.format(LIBG_X86), 'skip={}'.format(info['x86']['key-offset']), 'bs=1', 'count=32'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
try:
    result.check_returncode()
except subprocess.CalledProcessError as e:
    print('ERROR: Failed to get new x86 libg.so key.', file=sys.stderr)
    sys.exit(1)
else:
    if result.stdout.hex() != config['key']:
        print('ERROR: New x86 libg.so key is incorrect.', file=sys.stderr)
        sys.exit(1)

print('Verifying URLs ...')

result = subprocess.run([config['paths']['dd'], 'if={}'.format(LIBG_ARM), 'skip={}'.format(info['arm']['url-offset']), 'bs=1', 'count=22'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
try:
    result.check_returncode()
except subprocess.CalledProcessError as e:
    print('ERROR: Failed to get new arm libg.so URL.', file=sys.stderr)
    sys.exit(1)
else:
    try:
        result.stdout.decode()
    except UnicodeDecodeError as e:
        print('ERROR: Failed to get new arm libg.so URL.', file=sys.stderr)
        sys.exit(1)
    else:
        if result.stdout.decode().rstrip() != config['url']:
            print('ERROR: New arm libg.so URL is incorrect.', file=sys.stderr)
            sys.exit(1)

result = subprocess.run([config['paths']['dd'], 'if={}'.format(LIBG_X86), 'skip={}'.format(info['x86']['url-offset']), 'bs=1', 'count=22'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
try:
    result.check_returncode()
except subprocess.CalledProcessError as e:
    print('ERROR: Failed to get new x86 libg.so URL.', file=sys.stderr)
    sys.exit(1)
else:
    try:
        result.stdout.decode()
    except UnicodeDecodeError as e:
        print('ERROR: Failed to get new x86 libg.so URL.', file=sys.stderr)
        sys.exit(1)
    else:
        if result.stdout.decode().rstrip() != config['url']:
            print('ERROR: New x86 libg.so URL is incorrect.', file=sys.stderr)
            sys.exit(1)

print('Backing up original APK ...')

os.makedirs(BUILD_DIR, exist_ok=True)
shutil.move(APK_PATH, BACKUP_PATH)

print('Building APK ...')

result = subprocess.run([config['paths']['apktool'], 'b', '-o', UNSIGNED_PATH, DECODED_DIR], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
try:
    result.check_returncode()
except subprocess.CalledProcessError as e:
    if config['debug']:
        print('ERROR: Failed to build {} ({}).'.format(RELEASE_NAME, result.stderr.strip().rstrip('.').replace('{}/'.format(BASE_DIR), '')), file=sys.stderr)
    else:
        print('ERROR: Failed to build {}.'.format(RELEASE_NAME), file=sys.stderr)
    sys.exit(1)

print('Signing APK ...')

result = subprocess.run([config['paths']['jarsigner'], '-sigalg', 'SHA1withRSA', '-digestalg', 'SHA1', '-keystore', KEYSTORE_PATH, '-storepass', config['keystore']['storepass'], UNSIGNED_PATH, config['keystore']['key']['alias']], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
try:
    result.check_returncode()
except subprocess.CalledProcessError as e:
    if config['debug']:
        print('ERROR: Failed to build {} ({}).'.format(RELEASE_NAME, result.stderr.strip().rstrip('.').replace('{}/'.format(BASE_DIR), '')), file=sys.stderr)
    else:
        print('ERROR: Failed to build {}.'.format(RELEASE_NAME), file=sys.stderr)
    sys.exit(1)

shutil.move(UNSIGNED_PATH, UNALIGNED_PATH)

print('Aligning APK ...')

result = subprocess.run([config['paths']['zipalign'], '4', UNALIGNED_PATH, PATCHED_PATH], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
try:
    result.check_returncode()
except subprocess.CalledProcessError as e:
    if config['debug']:
        print('ERROR: Failed to build {} ({}).'.format(RELEASE_NAME, result.stderr.strip().rstrip('.').replace('{}/'.format(BASE_DIR), '')), file=sys.stderr)
    else:
        print('ERROR: Failed to build {}.'.format(RELEASE_NAME), file=sys.stderr)
    sys.exit(1)

shutil.rmtree(DECODED_DIR)

print('Done.')