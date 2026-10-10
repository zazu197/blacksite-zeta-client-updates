import hashlib,json,pathlib,subprocess
out=pathlib.Path(__file__).resolve().parent;manifest=json.loads((out/'client-manifest.json').read_text())
r=subprocess.run(['gh','api','repos/zazu197/blacksite-zeta-client-updates/releases/408467328'],capture_output=True,text=True,check=True)
release=json.loads(r.stdout);assets={a['name']:a for a in release['assets']};checks=[]
expected=[{'name':m['file'],'size':m['size'],'sha256':m['sha256']} for m in manifest['mods'] if not m['optional']]
expected.append({'name':manifest['configArchive']['file'],'size':manifest['configArchive']['size'],'sha256':manifest['configArchive']['sha256']})
for name in ['Install-Blacksite.bat','client-manifest.json','MODS.md','README.md','Electric-Blaze-Heaters.txt','Blacksite-Complete-Client-Star-1.1.0.zip','Blacksite-Complete-Client-Star-1.1.0.zip.sha256']:
 p=out/name;expected.append({'name':name,'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
names=json.loads((out/'release-asset-names.json').read_text())
for e in expected:
 a=assets.get(names.get(e['name'],e['name']));assert a,e['name']+' missing from release'
 assert a['state']=='uploaded' and a['size']==e['size'] and a['digest']=='sha256:'+e['sha256'],e['name']
 checks.append(e['name'])
report={'passed':True,'verifiedReleaseAssets':len(checks),'allGithubDigestsMatch':True,'releaseId':release['id'],'releaseUrl':'https://github.com/zazu197/blacksite-zeta-client-updates/releases/tag/client-star-1.1.0','draft':release['draft']}
(out/'release-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
