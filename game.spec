# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['game.py'],
             pathex=['C:\\Users\\maria\\pref'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
def extra_datas(mydir):
    def rec_glob(p, files):
        import os
        import glob
        for d in glob.glob(p):
            if os.path.isfile(d):
                files.append(d)
            else:
                rec_glob("%s/*" % d, files)
    files=[]
    rec_glob("%s/*" % mydir, files)
    extra_datas=[]
    for f in files:
        extra_datas.append((f, f))

a.datas = extra_datas('sprites')

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='pref',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
