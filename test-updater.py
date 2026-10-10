import collections,concurrent.futures,copy,hashlib,http.server,json,os,pathlib,shutil,subprocess,threading,uuid,zipfile
from urllib.parse import unquote,urlparse
out=pathlib.Path(__file__).resolve().parent;root=out.parent
test=out/'test-artifacts'/uuid.uuid4().hex[:8];test.mkdir(parents=True)
manifest=json.loads((out/'client-manifest.json').read_text());seen=[];checks=[]
sources={p.name:p for p in (out/'release-assets').iterdir()}
sources.update({m['file']:root/'unified-mods/client-mods'/m['file'] for m in manifest['mods'] if m['optional']})
sources.update({m['file']:root/'nuclear-update'/m['file'] for m in manifest['mods'] if m.get('authorDownload') and m['file'].startswith('createnuclear-')})
sources.update({m['file']:root/'create-restoration'/m['file'] for m in manifest['mods'] if m['file'].startswith('createbetterfps-')})
class Handler(http.server.BaseHTTPRequestHandler):
 def do_GET(self):
  name=unquote(urlparse(self.path).path.lstrip('/'));seen.append(name)
  if name.startswith('bad/'):
   data=b'not the expected jar';self.send_response(200);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
  p=sources.get(name)
  if not p:self.send_error(404);return
  self.send_response(200);self.send_header('Content-Length',str(p.stat().st_size));self.end_headers()
  with p.open('rb') as f:shutil.copyfileobj(f,self.wfile)
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/'
local=copy.deepcopy(manifest)
for m in local['mods']:m['url']=base+m['file']
local['configArchive']['url']=base+local['configArchive']['file']
manifestfile=test/'manifest.json';manifestfile.write_text(json.dumps(local))
env=dict(os.environ);env.update({'BLACKSITE_TEST_MODE':'1','BLACKSITE_NO_PAUSE':'1','BLACKSITE_TEST_MANIFEST':str(manifestfile),'USERPROFILE':str(test/'user'),'LOCALAPPDATA':str(test/'local'),'APPDATA':str(test/'appdata')});env.pop('OneDrive',None)
def check(ok,name):assert ok,name;checks.append(name)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(p=None,label='run',m=None):
 if m is not None:manifestfile.write_text(json.dumps(m))
 else:manifestfile.write_text(json.dumps(local))
 seen.clear();cmd='cmd.exe /d /c call "'+str(out/'Install-Blacksite.bat')+'"'+(' "'+str(p)+'"' if p else '')
 temporary_before={x.name for x in pathlib.Path(os.environ['TEMP']).glob('blacksite-scan-*')}
 r=subprocess.run(cmd,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=240)
 assert {x.name for x in pathlib.Path(os.environ['TEMP']).glob('blacksite-scan-*')}<=temporary_before,'Updater left a temporary download folder'
 (test/(label+'.log')).write_text(r.stdout+r.stderr)
 if r.returncode:print(label+': '+r.stdout[-1600:],flush=True)
 return r,list(seen)
def profile(name,complete=True):
 p=test/'Custom Minecraft/Instances'/name;(p/'mods').mkdir(parents=True)
 (p/'minecraftinstance.json').write_text(json.dumps({'gameVersion':'1.21.1','baseModLoader':{'name':'neoforge-21.1.250'}}))
 if complete:
  for m in manifest['mods']:os.link(sources[m['file']],p/'mods'/m['file'])
  with zipfile.ZipFile(sources[manifest['configArchive']['file']]) as z:
   for name in z.namelist():target=p/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(name))
 (p/'options.txt').write_text('my personal key bindings and graphics');(p/'saves/my-world').mkdir(parents=True);(p/'saves/my-world/level.dat').write_bytes(b'my world')
 return p
try:
 p=profile('Blacksite Repair')
 for name in ['Mekanism-1.21.1-10.7.19.85.jar','ConstructionSticks-1.21.1-1.5.0.jar']:(p/'mods'/name).unlink()
 corrupted=next(m for m in manifest['mods'] if m['name']=='Fzzy Config')['file'];(p/'mods'/corrupted).unlink();(p/'mods'/corrupted).write_bytes(b'wrong bytes')
 os.link(sources['ConstructionSticks-1.21.1-1.5.0.jar'],p/'mods/renamed-old-construction.jar')
 (p/'mods/dirt_slabs-1.0.0-neoforge-1.21.1.jar').write_bytes(b'old dirt');(p/'mods/blacksite-effects-1.3.0.jar').write_bytes(b'old effects')
 retired_disabled=['dirt_slabs-1.0.0-neoforge-1.21.1.jar.disabled','blacksite-effects-1.2.0.jar.disabled','blacksite-platform-1.4.0.jar.disabled']
 for name in retired_disabled:(p/'mods'/name).write_bytes(b'retired disabled copy')
 os.link(sources['ConstructionSticks-1.21.1-1.5.0.jar'],p/'mods/renamed-old-construction.jar.disabled')
 metadata=json.loads((p/'minecraftinstance.json').read_text());metadata['installedAddons']=[{'installedFile':{'fileName':name.replace('.disabled','')},'isEnabled':False} for name in retired_disabled+['renamed-old-construction.jar']]+[{'installedFile':{'fileName':'dirt_slabs-0.9.0.jar'},'isEnabled':True},{'installedFile':{'fileName':'create-player-addon-1.0.jar'},'isEnabled':True,'personalMetadata':42}];(p/'minecraftinstance.json').write_text(json.dumps(metadata))
 (p/'mods/my-personal-addon.jar.disabled').write_bytes(b'unrelated disabled mod')
 (p/'mods/create-player-addon-1.0.jar').write_bytes(b'unrelated custom addon')
 (p/'config/Mekanism/general.toml').write_text('maxUpgradeMultiplier = 10\n')
 (p/'config/create-client.toml').write_text('my personal Create rendering config')
 (p/'config/voxy-config.json').write_text(json.dumps({'enabled':True,'enable_rendering':True,'ingest_enabled':False,'section_render_distance':31.0,'customPreference':42}))
 (p/'config/create-server.toml').write_text('maxRotationSpeed = 256\nmyOtherSetting = 17\n')
 (p/'mods/createbetterfps-1.21.1-1.1.5.jar').unlink();(p/'mods/createbetterfps-1.21.1-1.1.5.jar').write_bytes(b'previous crashing optimizer')
 (p/'config/entityculling.json').write_text(json.dumps({'customPreference':17,'blockEntityWhitelist':['my:machine'],'entityWhitelist':[],'tickCullingWhitelist':[]}))
 r,requests=run(p,'repair');check(r.returncode==0,'Readable BAT executes in Windows PowerShell')
 check(set(requests)=={'Mekanism-1.21.1-10.7.19.85.jar','ConstructionSticks-1.21.1-1.5.0.jar',corrupted,'createbetterfps-1.21.1-1.1.5.jar',manifest['configArchive']['file']},'Only missing/corrupt mods and needed config archive downloaded')
 check(all(digest(p/'mods'/m['file'])==m['sha256'] for m in manifest['mods']),'All 287 required and four selected performance mod hashes correct')
 check(not (p/'mods/renamed-old-construction.jar').exists(),'Old mod version detected by real mod identity despite renamed JAR')
 check(not (p/'mods/dirt_slabs-1.0.0-neoforge-1.21.1.jar').exists() and not (p/'mods/blacksite-effects-1.3.0.jar').exists(),'Explicitly removed and superseded mods deleted')
 check(not any((p/'mods'/n).exists() for n in retired_disabled+['renamed-old-construction.jar.disabled']),'Retired disabled JARs and renamed old disabled mod versions removed')
 metadata=json.loads((p/'minecraftinstance.json').read_text());check(metadata['installedAddons']==[{'installedFile':{'fileName':'create-player-addon-1.0.jar'},'isEnabled':True,'personalMetadata':42}],'Retired CurseForge entries removed, including entries whose JAR was already deleted')
 check((p/'mods/my-personal-addon.jar.disabled').read_bytes()==b'unrelated disabled mod','Unrelated disabled player mod preserved')
 check((p/'mods/create-player-addon-1.0.jar').exists(),'Unrelated Create addon preserved')
 check((p/'options.txt').read_text()=='my personal key bindings and graphics' and (p/'saves/my-world/level.dat').read_bytes()==b'my world','Personal options and saves preserved')
 check((p/'config/create-client.toml').read_text()=='my personal Create rendering config','Personal optional config preserved')
 vc=json.loads((p/'config/voxy-config.json').read_text());check(vc['ingest_enabled'] and vc['section_render_distance']==31.0 and vc['customPreference']==42,'Voxy terrain collection enabled without overwriting personal preferences')
 check('maxRotationSpeed = 512' in (p/'config/create-server.toml').read_text() and 'myOtherSetting = 17' in (p/'config/create-server.toml').read_text(),'Only Create RPM setting changed in existing configuration')
 check(digest(p/'mods/createbetterfps-1.21.1-1.1.5.jar')==next(m['sha256'] for m in manifest['mods'] if m['file'].startswith('createbetterfps-')),'Create Better FPS restored and verified')
 check('maxUpgradeMultiplier = 16' in (p/'config/Mekanism/general.toml').read_text(),'Recent Mekanism multiplier installed')
 check(len(list((p/'config/ftbquests/quests/chapters').glob('*.snbt')))==66,'Complete recent quest update installed')
 ec=json.loads((p/'config/entityculling.json').read_text());check(ec['customPreference']==17 and 'my:machine' in ec['blockEntityWhitelist'],'Performance compatibility exceptions merged without resetting personal settings')
 check(not any('backup' in f.name.lower() for f in p.iterdir()),'No backup folder created')
 before={f.relative_to(p).as_posix():digest(f) for f in p.rglob('*') if f.is_file()}
 r,requests=run(p,'repeat');check(r.returncode==0 and not requests,'Repeated full scan downloads nothing when current')
 check(before=={f.relative_to(p).as_posix():digest(f) for f in p.rglob('*') if f.is_file()},'Repeated update is idempotent')
 fps=next(m for m in manifest['mods'] if m['file'].startswith('createbetterfps-'))
 disabled=p/'mods'/(fps['file']+'.disabled');(p/'mods'/fps['file']).rename(disabled)
 metadata=json.loads((p/'minecraftinstance.json').read_text());metadata['installedAddons']=[{'installedFile':{'fileName':fps['file']},'isEnabled':False,'personalMetadata':42}];(p/'minecraftinstance.json').write_text(json.dumps(metadata))
 r,requests=run(p,'enable-disabled');check(r.returncode==0 and not requests,'Disabled correct required mod restored without downloading it again')
 metadata=json.loads((p/'minecraftinstance.json').read_text());check(metadata['installedAddons'][0]['isEnabled'] and metadata['installedAddons'][0]['personalMetadata']==42 and not disabled.exists(),'CurseForge disabled flag updated while personal metadata is preserved')
 metadata['baseModLoader']['name']='neoforge-21.1.240';(p/'minecraftinstance.json').write_text(json.dumps(metadata))
 before={f.relative_to(p).as_posix():digest(f) for f in p.rglob('*') if f.is_file()};r,requests=run(p,'wrong-loader');check(r.returncode!=0 and not requests,'Incorrect CurseForge loader rejected before downloading')
 check(before=={f.relative_to(p).as_posix():digest(f) for f in p.rglob('*') if f.is_file()},'Rejected loader changes no profile files')
 metadata['baseModLoader']['name']='neoforge-21.1.250';(p/'minecraftinstance.json').write_text(json.dumps(metadata))
 bad=copy.deepcopy(local);next(m for m in bad['mods'] if m['file']=='ConstructionSticks-1.21.1-1.5.0.jar')['url']=base+'bad/ConstructionSticks.jar'
 (p/'mods/ConstructionSticks-1.21.1-1.5.0.jar').unlink();before={f.relative_to(p).as_posix():digest(f) for f in p.rglob('*') if f.is_file()}
 r,_=run(p,'bad-download',bad);check(r.returncode!=0,'Bad download rejected by SHA256')
 check(before=={f.relative_to(p).as_posix():digest(f) for f in p.rglob('*') if f.is_file()},'Failed download changes no profile files')
 os.link(sources['ConstructionSticks-1.21.1-1.5.0.jar'],p/'mods/ConstructionSticks-1.21.1-1.5.0.jar')
 bad=copy.deepcopy(local);bad['files'][0]['path']='../options.txt';r,_=run(p,'bad-path',bad);check(r.returncode!=0,'Unsafe manifest path rejected')
 empty=profile('Magitech Empty',False)
 settings=test/'appdata/CurseForge';settings.mkdir(parents=True);(settings/'storage.json').write_text(json.dumps({'minecraft-settings':json.dumps({'minecraftRoot':str(empty.parent.parent)})}))
 # The repaired fixture moves outside discovery so the empty named profile is unique.
 moved=test/'repaired-profile';shutil.move(str(p),moved)
 other=profile('All the Mods 10 - ATM10');(other/'mods/blacksite-platform-1.4.1.jar').unlink()
 other_before={f.relative_to(other).as_posix():digest(f) for f in other.rglob('*') if f.is_file()}
 r,requests=run(None,'fresh-auto');check(r.returncode==0,'Empty named NeoForge profile discovered through custom CurseForge folder')
 check(other_before=={f.relative_to(other).as_posix():digest(f) for f in other.rglob('*') if f.is_file()},'Unrelated ATM10 profile was not selected or changed')
 check(len([x for x in requests if x.endswith('.jar')])==291,'Fresh profile downloads complete mod list')
 check(all(digest(empty/'mods'/m['file'])==m['sha256'] for m in manifest['mods']),'Fresh install verifies every required and optimization mod')
 check(len(list((empty/'config/ftbquests/quests/chapters').glob('*.snbt')))==66 and (empty/'blacksite-guides/Electric-Blaze-Heaters.txt').exists(),'Fresh install receives quest book and Electric Blaze instructions')
 check(not (empty/'.blacksite-backups').exists(),'Fresh install creates no backups')
 report={'passed':True,'checks':checks,'downloadsUseRealHTTP':True,'powershell':'Windows PowerShell 5.1','modFilesVerified':len(manifest['mods']),'liveServerWrites':0}
 (out/'installer-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'checks':len(checks),'testDirectory':str(test)}),flush=True)
finally:server.shutdown()
