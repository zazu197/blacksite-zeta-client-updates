import json,pathlib,re
from urllib.parse import urlparse
out=pathlib.Path(__file__).resolve().parent;m=json.loads((out/'client-manifest.json').read_text())
assert m['schemaVersion']==1 and m['minecraft']=='1.21.1' and m['neoforge']=='21.1.250'
assert len(m['mods'])==291 and sum(not x['optional'] for x in m['mods'])==287
paths=set();ids=set()
for x in m['mods']:
 assert '/' not in x['file'] and '\\' not in x['file'] and x['file'].endswith('.jar')
 assert re.fullmatch('[a-f0-9]{64}',x['sha256']) and x['size']>0 and x['file'] not in paths;paths.add(x['file'])
 u=urlparse(x['url']);assert u.scheme=='https'
 assert (u.netloc=='cdn.modrinth.com' and x['optional']) or (u.netloc=='github.com' and u.path.startswith('/zazu197/blacksite-zeta-client-updates/releases/download/client-star-')) or (u.netloc=='edge.forgecdn.net' and x.get('authorDownload'))
 for id in x['modIds']:assert id not in ids;ids.add(id)
paths=set()
for x in m['files']:
 p=pathlib.PurePosixPath(x['path']);assert '..' not in p.parts and ':' not in x['path'] and '\\' not in x['path']
 assert p.parts[0] in ['config','defaultconfigs','kubejs','resourcepacks','shaderpacks','configureddefaults','blacksite-guides']
 assert x['path'] not in paths and re.fullmatch('[a-f0-9]{64}',x['sha256']) and x['size']>=0;paths.add(x['path'])
 assert x['policy'] in ['replace','ifMissing','mergeJsonArrays']
assert 'blacksite_ars_equipment_counters' in ids and 'dirt_slabs' not in ids
assert 'constructionstick' in ids and 'doubleslabs' in ids and 'create_electric_blaze' in ids
assert len([p for p in paths if p.startswith('config/ftbquests/quests/chapters/')])==66
assert next(x for x in m['files'] if x['path']=='config/create_electric_blaze-common.toml')['policy']=='replace'
assert json.loads((out/'installer-verification.json').read_text())['passed']
assert json.loads((out/'package-verification.json').read_text())['passed']
print('Validated complete client manifest, 287 required and four optional mod files, 66 quest chapters, and verified no-backup updater.')
