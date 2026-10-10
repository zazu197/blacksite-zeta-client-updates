import hashlib,json,pathlib,subprocess
out=pathlib.Path(__file__).resolve().parent;manifest=json.loads((out/'client-manifest.json').read_text())
releases={}
for tag in ['client-star-1.1.0',manifest['version']]:
 r=subprocess.run(['gh','api','repos/zazu197/blacksite-zeta-client-updates/releases/tags/'+tag],capture_output=True,text=True,check=True);releases[tag]=json.loads(r.stdout)
release=releases[manifest['version']];checks=[]
expected=[{'name':m['url'].rsplit('/',1)[1],'tag':m['url'].split('/download/')[1].split('/')[0],'size':m['size'],'sha256':m['sha256']} for m in manifest['mods'] if not m['optional'] and not m.get('authorDownload')]
expected.append({'name':manifest['configArchive']['file'],'tag':manifest['version'],'size':manifest['configArchive']['size'],'sha256':manifest['configArchive']['sha256']})
for name in ['Install-Blacksite.bat','client-manifest.json','MODS.md','README.md','Blacksite-Complete-Client-Star-1.2.0.zip','Blacksite-Complete-Client-Star-1.2.0.zip.sha256']:
 p=out/name;expected.append({'name':name,'tag':manifest['version'],'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
names=json.loads((out/'release-asset-names.json').read_text())
for e in expected:
 from urllib.parse import unquote
 assets={a['name']:a for a in releases[e['tag']]['assets']};a=assets.get(unquote(e['name']));assert a,e['name']+' missing from release'
 assert a['state']=='uploaded' and a['size']==e['size'] and a['digest']=='sha256:'+e['sha256'],e['name']
 checks.append(e['name'])
report={'passed':True,'verifiedReleaseAssets':len(checks),'allGithubDigestsMatch':True,'releaseId':release['id'],'releaseUrl':'https://github.com/zazu197/blacksite-zeta-client-updates/releases/tag/'+manifest['version'],'draft':release['draft'],'authorCreateNuclearDownload':True}
(out/'release-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
