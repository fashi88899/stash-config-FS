# -*- coding: utf-8 -*-
"""
Stash 一机一IP · 最终稳定专业版 v9_pro
------------------------------------------------------
✅ 自动读取手机IP列表.xlsx
✅ 自动生成 stash_X.yaml（内联IP）
✅ 自动生成二维码（带时间戳 ?v= 参数防缓存）
✅ 自动执行 Git 同步（reset→pull→push）
✅ 自动备份 output/ 目录（最多保留3份）
"""

import os, pandas as pd, yaml, qrcode, subprocess, shutil
from pathlib import Path
from datetime import datetime

REPO_PATH = r"C:\Users\fashi\stash-config-FS"
CDN_BASE = "https://cdn.jsdelivr.net/gh/fashi88899/stash-config-FS@main/output"

OUTPUT_DIR = os.path.join(REPO_PATH, "output")
EXCEL_FILE = os.path.join(REPO_PATH, "手机IP列表.xlsx")
BACKUP_DIR = os.path.join(REPO_PATH, "backups")

def ensure_dirs():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)

def load_rows():
    df = pd.read_excel(EXCEL_FILE)
    rows = []
    for _, r in df.iterrows():
        rows.append({
            "id": int(r["手机编号"]),
            "ip": str(r["IP"]).strip(),
            "port": int(r["端口"]),
            "user": str(r["用户名"]).strip(),
            "pwd": str(r["密码"]).strip(),
        })
    return rows

def write_stash_inline(i, ip, port, user, pwd):
    data = {
        "mode": "Rule",
        "log-level": "info",
        "allow-lan": True,
        "proxies": [{
            "name": f"Phone{i}",
            "type": "socks5",
            "server": ip,
            "port": int(port),
            "username": user,
            "password": pwd,
        }],
        "proxy-groups": [{
            "name": "Proxy",
            "type": "select",
            "use": [f"Phone{i}"]
        }],
        "rules": [
            "DOMAIN-SUFFIX,whatsapp.net,Proxy",
            "DOMAIN-SUFFIX,whatsapp.com,Proxy",
            "IP-CIDR,31.13.64.0/18,Proxy",
            "MATCH,Proxy"
        ]
    }
    path = os.path.join(OUTPUT_DIR, f"stash_{i}.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, indent=2)
    return path

def make_qr(i, version_tag):
    url = f"{CDN_BASE}/stash_{i}.yaml?v={version_tag}"
    img = qrcode.make(url)
    path = os.path.join(OUTPUT_DIR, f"QR_Phone{i}_{version_tag}.png")
    img.save(path)
    return path, url

def run(cmd, cwd=None):
    subprocess.run(cmd, cwd=cwd, check=False, text=True)

def git_sync():
    run(["git", "checkout", "main"], cwd=REPO_PATH)
    run(["git", "reset", "--hard"], cwd=REPO_PATH)
    run(["git", "fetch", "origin"], cwd=REPO_PATH)
    run(["git", "pull", "origin", "main", "--rebase"], cwd=REPO_PATH)
    run(["git", "add", "."], cwd=REPO_PATH)
    run(["git", "commit", "-m", "Auto update (v9_pro)"], cwd=REPO_PATH)
    run(["git", "push", "origin", "main", "--force"], cwd=REPO_PATH)
    print("🚀 Git 同步完成。")

def rotate_backups(version_tag):
    dst = os.path.join(BACKUP_DIR, f"output_{version_tag}.zip")
    shutil.make_archive(dst.replace('.zip',''), 'zip', OUTPUT_DIR)
    zips = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.zip')])
    while len(zips) > 3:
        os.remove(os.path.join(BACKUP_DIR, zips.pop(0)))

def main():
    ensure_dirs()
    rows = load_rows()
    version_tag = datetime.now().strftime("%Y%m%d%H%M%S")
    for r in rows:
        p = write_stash_inline(r["id"], r["ip"], r["port"], r["user"], r["pwd"])
        qr, url = make_qr(r["id"], version_tag)
        print(f"✅ 生成 Phone{r['id']}：{url}\n📄 {p}\n🧾 {qr}\n")
    rotate_backups(version_tag)
    git_sync()

if __name__ == "__main__":
    main()
