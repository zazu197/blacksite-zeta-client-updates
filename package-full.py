import hashlib,json,pathlib,zipfile
out=pathlib.Path(__file__).resolve().parent;root=out.parent
manifest=json.loads((out/'client-manifest.json').read_text())
entries={}
with zipfile.ZipFile(root/'quest-refresh/Blacksite-Complete-Client-Star-Update.zip') as z:
 for name in z.namelist():
  if name in ['Install-Client-Optimizations.ps1','Install-Blacksite.bat','README.txt','client-files.json']:continue
  entries[name]=z.read(name)
with zipfile.ZipFile(out/'release-assets/Blacksite-Client-Files.zip') as z:
 for name in z.namelist():entries['client/'+name]=z.read(name)
for name in ['Install-Blacksite.bat','client-manifest.json','MODS.md','README.md','Electric-Blaze-Heaters.txt']:entries[name]=(out/name).read_bytes()
entries['README.txt']=('BLACKSITE ZETA COMPLETE CLIENT - STAR 1.1.0\n\n'
 'Minecraft 1.21.1 / NeoForge 21.1.250 / Java 21\n'
 'All 286 required mod JARs, configs, resources, quests, and pending Mekanism/GUI changes are included.\n'
 'The matching server changes remain staged. Wait for activation before joining.\n\n'
 'EXISTING PROFILE: Close Minecraft and run Install-Blacksite.bat. It downloads the latest manifest\n'
 'from zazu197/blacksite-zeta-client-updates on GitHub and checks every required mod.\n'
 'Only missing/wrong mods and required client-file changes are downloaded and installed.\n'
 'Four optional performance mods are downloaded directly from their authors by default.\n'
 'It creates NO BACKUPS. Saves, personal options and unrelated mods are preserved.\n'
 'The same BAT can be rerun to check and repair the complete client in the future.\n\n'
 'FRESH PROFILE: Import this ZIP into CurseForge. Optional performance mods can then be\n'
 'installed by running the BAT. The launcher supplies Minecraft, NeoForge and Java.\n'
 'Read README.md and MODS.md for details.\n\n'
 'ELECTRIC BLAZE SUPERHEAT: Apply a second Blaze Capacitor to the electric heater, supply\n'
 'at least 1,063 FE/t continuously and remove redstone signals. No new mod is required.\n'
 'Read Electric-Blaze-Heaters.txt.\n\n'
 'Public repo: https://github.com/zazu197/blacksite-zeta-client-updates\n').encode()
required={m['file']:m for m in manifest['mods'] if not m['optional']}
assert len([n for n in entries if n.startswith('client/mods/')])==286
for name,m in required.items():
 if not m.get('authorDownload'):assert hashlib.sha256(entries['client/mods/'+name]).hexdigest()==m['sha256']
for f in manifest['files']:assert hashlib.sha256(entries['client/'+f['path']]).hexdigest()==f['sha256']
entries['manifest.json']=json.dumps({'minecraft':{'version':'1.21.1','modLoaders':[{'id':'neoforge-21.1.250','primary':True}]},'manifestType':'minecraftModpack','manifestVersion':1,'name':'Blacksite Zeta','version':manifest['version'],'author':'Blacksite Zeta','files':[{'projectID':989797,'fileID':9056910,'required':True}],'overrides':'client'},indent=2).encode()
entries['README.txt']=entries['README.txt'].replace(b'STAR 1.1.0',b'STAR 1.2.0').replace(b'All 286 required mod JARs,',b'All 287 required mods (286 bundled; Create Nuclear downloaded by CurseForge or the BAT),').replace(b'The matching server changes remain staged. Wait for activation before joining.',b'Check the latest client manifest for server activation status.').replace(b'pending Mekanism/GUI',b'Mekanism/GUI')
p=out/'Blacksite-Complete-Client-Star-1.2.0.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for name,data in sorted(entries.items()):z.writestr(name,data)
with zipfile.ZipFile(p) as z:assert z.testzip() is None
report={'passed':True,'filename':p.name,'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'requiredMods':287,'bundledModJars':286,'requiredAuthorDownloads':1,'optionalAuthorDownloads':4,'questChapters':66,'newQuests':91,'noBackupInstaller':True,'activationPending':manifest['activationPending']}
(out/'package-verification.json').write_text(json.dumps(report,indent=2)+'\n');(out/(p.name+'.sha256')).write_text(report['sha256']+'  '+p.name+'\n');print(json.dumps(report),flush=True)
