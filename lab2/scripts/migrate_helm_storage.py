"""Copy only our Helm release history from Secrets to ConfigMaps, without deleting it."""
import argparse
import base64
import gzip
import json
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--namespace', default='itmo-student-06')
parser.add_argument('--apply', action='store_true')
args = parser.parse_args()
for release in ('pinchuk-search-staging', 'pinchuk-search-prod'):
    command = ['kubectl', '-n', args.namespace]
    raw = subprocess.check_output(command + ['get', 'secret', '-l', f'owner=helm,name={release}', '-o', 'json'])
    records = json.loads(raw)['items']
    if not records:
        raise SystemExit(f'No Helm history for {release}')
    for record in records:
        metadata = record['metadata']
        encoded = base64.b64decode(record['data']['release']).decode('ascii')
        release_data = json.loads(gzip.decompress(base64.b64decode(encoded)))
        if release_data['name'] != release or release_data['namespace'] != args.namespace:
            raise SystemExit('Release identity mismatch')
        configmap = {
            'apiVersion': 'v1', 'kind': 'ConfigMap',
            'metadata': {'name': metadata['name'], 'namespace': args.namespace,
                         'labels': metadata['labels']},
            'data': {'release': encoded},
        }
        lookup = subprocess.run(command + ['get', 'configmap', metadata['name'], '-o', 'json', '--ignore-not-found'],
                                capture_output=True, text=True, check=True)
        if lookup.stdout.strip():
            existing = json.loads(lookup.stdout)
            if existing.get('data', {}).get('release') != encoded:
                raise SystemExit(f'Conflicting ConfigMap: {metadata["name"]}')
        elif args.apply:
            subprocess.run(command + ['create', '-f', '-'], input=json.dumps(configmap), text=True,
                           check=True, stdout=subprocess.DEVNULL)
        print(f'{release}: revision {release_data["version"]} checked')
