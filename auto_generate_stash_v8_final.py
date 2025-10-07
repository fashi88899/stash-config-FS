# -*- coding: utf-8 -*-
"""
Stash 一机一IP · 最终一键版 v8_final (2台设备示例)
"""

import os, pandas as pd, yaml, qrcode, subprocess
from pathlib import Path
from datetime import datetime

REPO_PATH = r"C:\Users\fashi\stash-config-FS"
CDN_BASE  = "https://cdn.jsdelivr.net/gh/fashi88899/stash-config-FS@main/output"
OUTPUT_DIR = os.path.join(REPO_PATH, "output")
EXCEL_FILE = os.path.join(REPO_PATH, "手机IP列表.xlsx")

def ensure_dirs():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def load_rows():
    df = pd.read_excel(EXCEL_FILE)
    return [{
        "id": int(r["手机编号"]),
        "ip": str(r["IP"]).strip(),
        "port": int(r["端口"]),
        "user": str(r["用户名"]).strip(),
        "pwd": str(r["密码"]).strip()
    } for _, r in df.iterrows()]

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
            "password": pwd
        }],
        "proxy-groups": [{
            "name": "Proxy",
            "type": "select",
            "use": [f"Phone{i}"]
        }],
        "rules": ["MATCH,Proxy"]
    }
    path = os.path.join(OUTPUT_DIR, f"stash_{i}.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, indent=2, default_flow_style=False)
    return path

def make_qr(i, version_tag):
    url = f"{CDN_BASE}/stash_{i}.yaml?v={version_tag}"
    img = qrcode.make(url)
    path = os.path.join(OUTPUT_DIR, f"QR_Phone{i}.png")
    img.save(path)
    return path, url

def git_sync():
    cmds = [
        ["git", "fetch", "origin"],
        ["git", "pull", "origin", "main", "--rebase"],
        ["git", "add", "."],
        ["git", "commit", "-m", "Auto update (v8_final)"],
        ["git", "push", "origin", "main", "--force"]
    ]
    for cmd in cmds:
        subprocess.run(cmd, cwd=REPO_PATH, text=True)
    print("🚀 Git 同步完成。")

def main():
    ensure_dirs()
    rows = load_rows()
    version_tag = datetime.now().strftime("%Y%m%d%H%M%S")
    for r in rows:
        p = write_stash_inline(r["id"], r["ip"], r["port"], r["user"], r["pwd"])
        qr, url = make_qr(r["id"], version_tag)
        print(f"✅ 生成 Phone{r['id']}：{url}\n📄 {p}\n🧾 {qr}\n")
    git_sync()

if __name__ == "__main__":
    main()
