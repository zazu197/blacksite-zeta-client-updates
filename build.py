import hashlib,io,json,pathlib,re,sys,tomllib,zipfile
from urllib.parse import quote
out=pathlib.Path(__file__).resolve().parent
root=out.parent
repo='zazu197/blacksite-zeta-client-updates'
tag='client-star-1.1.0'
assets=out/'release-assets';assets.mkdir(exist_ok=True)
def sha(data):return hashlib.sha256(data).hexdigest()
def meta(data,filename):
 with zipfile.ZipFile(io.BytesIO(data)) as z:
  for name in ['META-INF/neoforge.mods.toml','META-INF/mods.toml']:
   if name in z.namelist():
    d=tomllib.loads(z.read(name).decode());mods=d.get('mods',[])
    return {'name':' / '.join(m.get('displayName',m['modId']) for m in mods),'modIds':[m['modId'] for m in mods]}
  if 'fabric.mod.json' in z.namelist():
   d=json.loads(z.read('fabric.mod.json'));return {'name':d.get('name',d['id']),'modIds':[d['id']]}
 if filename.startswith(('connector-','kotlinforforge-')):
  return {'name':'Sinytra Connector bootstrap' if filename.startswith('connector-') else 'Kotlin for Forge language provider','modIds':[]}
 raise ValueError('No mod identity: '+filename)
def url(file):return 'https://github.com/'+repo+'/releases/download/'+tag+'/'+quote(file,safe='')
source=root/'quest-refresh/Blacksite-Complete-Client-Star-Update.zip'
manifest=json.loads((root/'quest-refresh/client-files.json').read_text())
mods=[];settings={}
with zipfile.ZipFile(source) as z:
 for f in manifest['files']:
  data=z.read('client/'+f['path']);assert len(data)==f['size'] and sha(data)==f['sha256']
  if f['path'].startswith('mods/'):
   name=pathlib.PurePosixPath(f['path']).name;(assets/name).write_bytes(data)
   mods.append({'file':name,'size':len(data),'sha256':sha(data),'url':url(name),'optional':False,**meta(data,name)})
  else:settings[f['path']]=data
 guide=('ELECTRIC BLAZE HEATERS - SUPERHEATING\n\n'
        '1. Right-click a normal Blaze Burner with one Blaze Capacitor to make an Electric Blaze Heater.\n'
        '2. Right-click that electric heater with a SECOND Blaze Capacitor. Two capacitors enable superheating.\n'
        '3. Connect an FE energy cable and supply at least 1,063 FE/t continuously with the pack defaults.\n'
        '4. Remove any redstone signal: redstone disables the heater.\n'
        'Two powered capacitors produce the blue SEETHING heat used by Create superheated recipes.\n'
        'One capacitor uses 505 FE/t and produces ordinary KINDLED heat. No Blaze Cakes are needed.\n'
        'There is no new addon or server restart needed for this existing feature.\n\n'
        'Source: https://www.curseforge.com/minecraft/mc-mods/create-electric-blaze\n').encode()
 settings['blacksite-guides/Electric-Blaze-Heaters.txt']=guide
 # Make the known two-capacitor default part of the required client configuration.
 heater='config/create_electric_blaze-common.toml'
 assert re.search(rb'blaze_burner_max_capacitors\s*=\s*2',settings[heater])
 configrows=[dict(f) for f in manifest['files'] if not f['path'].startswith('mods/')]
 next(f for f in configrows if f['path']==heater)['policy']='replace'
 configrows.append({'path':'blacksite-guides/Electric-Blaze-Heaters.txt','size':len(guide),'sha256':sha(guide),'policy':'replace'})
opt=json.loads((root/'unified-mods/client-optimizations.json').read_text())
for m in opt['mods']:
 p=root/'unified-mods/client-mods'/m['file'];data=p.read_bytes();assert sha(data)==m['sha256'] and len(data)==m['size']
 mods.append({k:m[k] for k in ['file','size','sha256','url']}|{'optional':True,**meta(data,m['file'])})
 # Optional optimizations are installed directly from the authors, not redistributed.
optconfig=(root/'unified-mods/optimization-config/entityculling.json').read_bytes()
settings['config/entityculling.json']=optconfig
row=next((f for f in configrows if f['path']=='config/entityculling.json'),None)
mergekeys=['blockEntityWhitelist','entityWhitelist','tickCullingWhitelist']
newrow={'path':'config/entityculling.json','size':len(optconfig),'sha256':sha(optconfig),'policy':'mergeJsonArrays','mergeKeys':mergekeys,'requiredArrays':{k:json.loads(optconfig).get(k,[]) for k in mergekeys},'optional':True}
if row:configrows.remove(row)
configrows.append(newrow)
configzip=assets/'Blacksite-Client-Files.zip'
with zipfile.ZipFile(configzip,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for name,data in sorted(settings.items()):z.writestr(name,data)
with zipfile.ZipFile(configzip) as z:assert z.testzip() is None
configdata=configzip.read_bytes()
ids=[id for m in mods for id in m['modIds']];assert len(ids)==len(set(ids)),[x for x in ids if ids.count(x)>1]
assert len(mods)==290 and len([m for m in mods if not m['optional']])==286
release={'schemaVersion':1,'minimumInstallerVersion':1,'version':tag,'minecraft':'1.21.1','neoforge':'21.1.250','activationPending':True,'requiredModCount':286,'optionalModCount':4,'mods':mods,'files':configrows,'configArchive':{'file':configzip.name,'size':len(configdata),'sha256':sha(configdata),'url':url(configzip.name)},'removePrefixes':['dirt_slabs-','blacksite-effects-','blacksite-platform-'],'keepFiles':['blacksite-platform-1.4.0.jar'],'modPrefixes':manifest['modPrefixes']}
(out/'client-manifest.json').write_text(json.dumps(release,indent=2)+'\n')
lines=['# Blacksite Zeta client mods','','Minecraft 1.21.1 / NeoForge 21.1.250. **286 required pack JARs**, plus 4 optional client optimizations installed by default.','','Every download is pinned by exact filename, size, SHA-256 and mod identity in [client-manifest.json](client-manifest.json).','','| Mod | JAR | Installation |','| --- | --- | --- |']
for m in sorted(mods,key=lambda m:m['name'].lower()):lines.append('| '+m['name'].replace('|','/')+' | `'+m['file']+'` | '+('Optional performance' if m['optional'] else 'Required')+' |')
(out/'MODS.md').write_text('\n'.join(lines)+'\n')
(out/'Electric-Blaze-Heaters.txt').write_bytes(guide)
print(json.dumps({'mods':len(mods),'files':len(configrows),'configurationZipBytes':len(configdata),'releaseAssetBytes':sum(p.stat().st_size for p in assets.iterdir()),'repository':repo,'version':tag}))
