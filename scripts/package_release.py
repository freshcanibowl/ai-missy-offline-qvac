
"""Package source only; never ship node_modules, evidence, secrets, DB or patient files."""
import pathlib,zipfile,hashlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
DENY={'.env','node_modules','local-evidence','__pycache__','.git','.venv','.DS_Store'}
EXTS={'.sqlite3','.db','.pyc','.log','.jsonl','.zip','.mp4','.mov','.pem','.key'}
def package(out):
    out=pathlib.Path(out).resolve()
    files=[]
    for p in ROOT.rglob('*'):
        if not p.is_file() or any(x in DENY or x.startswith('.env') for x in p.relative_to(ROOT).parts):continue
        if p.suffix.lower() in EXTS or p.name=='package-lock.json' and False:continue
        if p.resolve()==out:continue
        files.append(p)
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(files):z.write(p,arcname='AI_Missy_Offline_Build07/'+p.relative_to(ROOT).as_posix())
    return len(files),hashlib.sha256(out.read_bytes()).hexdigest()
if __name__=='__main__':
    out=sys.argv[1] if len(sys.argv)>1 else str(ROOT.parent/'AI_Missy_Offline_Build07.zip')
    count,hash_=package(out)
    print(f'BUILD07_PACKAGE_FILES={count}');print(f'BUILD07_PACKAGE_SHA256={hash_}');print(f'BUILD07_PACKAGE={out}')
