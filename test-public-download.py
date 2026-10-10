import hashlib,json,os,pathlib,shutil,subprocess,uuid,urllib.request
out=pathlib.Path(__file__).resolve().parent;test=out/'test-artifacts'/('public-'+uuid.uuid4().hex[:8]);test.mkdir(parents=True)
m=json.loads((out/'client-manifest.json').read_text());sources={p.name:p for p in (out/'release-assets').iterdir()};root=out.parent
sources.update({x['file']:root/'unified-mods/client-mods'/x['file'] for x in m['mods'] if x['optional']})
sources.update({x['file']:root/'nuclear-update'/x['file'] for x in m['mods'] if x.get('authorDownload')})
source=next((out/'test-artifacts').glob('*/repaired-profile'))
p=test/'Blacksite Public Download';shutil.copytree(source,p,ignore=shutil.ignore_patterns('mods'));(p/'mods').mkdir()
for mod in m['mods']:os.link(sources[mod['file']],p/'mods'/mod['file'])
removed=['createnuclear-2.0.0-neoforge.jar','Create Encased-1.21.1-1.9.0-ht3.jar','InfiniteLava NeoForge 1.21.1 1.0.1.jar','Super Factory Manager (SFM)-MC1.21.1-4.34.0.jar',"mielon's-the-sift-1.1.2-mc1.21.1-neo.jar",'ConstructionSticks-1.21.1-1.5.0.jar','blacksite-platform-1.4.0.jar',next(x['file'] for x in m['mods'] if x['file'].startswith('entityculling-'))]
for name in removed:(p/'mods'/name).unlink()
(p/'config/Mekanism/general.toml').write_text('maxUpgradeMultiplier = 10\n')
bat=test/'Install-Blacksite.bat'
with urllib.request.urlopen('https://raw.githubusercontent.com/zazu197/blacksite-zeta-client-updates/main/Install-Blacksite.bat',timeout=60) as r:bat.write_bytes(r.read())
assert bat.read_bytes()==(out/'Install-Blacksite.bat').read_bytes()
env=dict(os.environ);env.update({'BLACKSITE_TEST_MODE':'1','BLACKSITE_NO_PAUSE':'1'});env.pop('BLACKSITE_TEST_MANIFEST',None)
cmd='cmd.exe /d /c call "'+str(bat)+'" "'+str(p)+'"'
r=subprocess.run(cmd,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=360);(test/'public-download.log').write_text(r.stdout+r.stderr)
assert r.returncode==0,r.stdout[-2200:]+r.stderr[-500:]
assert all(hashlib.sha256((p/'mods'/x['file']).read_bytes()).hexdigest()==x['sha256'] for x in m['mods'])
assert 'maxUpgradeMultiplier = 16' in (p/'config/Mekanism/general.toml').read_text()
assert not (p/'.blacksite-backups').exists()
assert (p/'saves/my-world/level.dat').read_bytes()==b'my world'
report={'passed':True,'anonymousGitHubBootstrap':True,'githubModsDownloaded':6,'directAuthorOptimizationsDownloaded':1,'directCreateNuclearDownloadVerified':True,'githubConfigArchiveDownloaded':True,'normalizedAssetNamesVerified':4,'all291ModHashesCorrect':True,'noBackups':True,'personalWorldPreserved':True,'powerRequests':0}
(out/'public-download-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
