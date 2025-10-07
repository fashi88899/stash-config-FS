# -*- coding: utf-8 -*-
import os, pandas as pd, yaml, qrcode
from pathlib import Path

REPO_PATH = os.getcwd()
CDN_BASE = "https://cdn.jsdelivr.net/gh/fashi88899/stash-config-FS@main/output"
OUTPUT_DIR = os.path.join(REPO_PATH, "output")
PROVIDERS_DIR = os.path.join(OUTPUT_DIR, "providers")
EXCEL_FILE = os.path.join(REPO_PATH, "手机IP列表.xlsx")

def ensure_dirs():
    Path(PROVIDERS_DIR).mkdir(parents=True, exist_ok=True)

def load_excel():
    df = pd.read_excel(EXCEL_FILE)
    rows = []
    for _, r in df.iterrows():
        rows.append({
            "id": int(r["手机编号"]), "ip": str(r["IP"]).strip(),
            "port": int(r["端口"]), "user": str(r["用户名"]).strip(), "pwd": str(r["密码"]).strip()
        })
    return rows

def write_proxy_yaml(i, ip, port, user, pwd):
    data = {"proxies": [{
        "name": f"Phone{i}", "type": "socks5", "server": ip,
        "port": int(port), "username": user, "password": pwd
    }]}
    path = os.path.join(PROVIDERS_DIR, f"proxy_{i}.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    return path

def write_stash_yaml(i):
    data = {
        "mode": "Rule", "log-level": "info", "allow-lan": True,
        "proxy-providers": {f"phone{i}": {
            "type": "http", "url": f"{CDN_BASE}/providers/proxy_{i}.yaml",
            "interval": 3600, "path": f"./providers/phone{i}.yaml"}},
        "proxy-groups": [{"name": "Proxy", "type": "select", "use": [f"phone{i}"]}],
        "rules": ["MATCH,Proxy"]
    }
    path = os.path.join(OUTPUT_DIR, f"stash_{i}.yaml")
    yaml.SafeDumper.ignore_aliases = lambda *args: True
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, indent=2, default_flow_style=False)
    return path

def make_qr(i):
    url = f"{CDN_BASE}/stash_{i}.yaml"
    img = qrcode.make(url)
    path = os.path.join(OUTPUT_DIR, f"QR_Phone{i}.png")
    img.save(path)
    return path, url

def main():
    ensure_dirs()
    rows = load_excel()
    for r in rows:
        write_proxy_yaml(r["id"], r["ip"], r["port"], r["user"], r["pwd"])
        stash_path = write_stash_yaml(r["id"])
        qr_path, url = make_qr(r["id"])
        print(f"✅ 生成 Phone{r['id']}：{url}\n📄 {stash_path}\n🧾 {qr_path}\n")

if __name__ == "__main__":
    main()
