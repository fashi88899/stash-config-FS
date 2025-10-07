# -*- coding: utf-8 -*-
import os, pandas as pd, yaml, qrcode, json, time, subprocess
from pathlib import Path

REPO_PATH = r"C:\Users\fashi\stash-config-FS"
CDN_BASE = "https://cdn.jsdelivr.net/gh/fashi88899/stash-config-FS@main/output"
OUTPUT_DIR = os.path.join(REPO_PATH, "output")
PROVIDERS_DIR = os.path.join(OUTPUT_DIR, "providers")
EXCEL_FILE = os.path.join(REPO_PATH, "手机IP列表.xlsx")
STATE_FILE = os.path.join(REPO_PATH, ".last_update.json")

def ensure_dirs():
    Path(PROVIDERS_DIR).mkdir(parents=True, exist_ok=True)

def get_excel_timestamp():
    if not os.path.exists(EXCEL_FILE):
        return 0
    return int(os.path.getmtime(EXCEL_FILE))

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

def git_push():
    try:
        subprocess.run(["git", "add", "."], cwd=REPO_PATH)
        subprocess.run(["git", "commit", "-m", "Auto update stash/proxy files (v5 autoPush)"], cwd=REPO_PATH)
        subprocess.run(["git", "push"], cwd=REPO_PATH)
        print("🚀 已自动推送至 GitHub。")
    except Exception as e:
        print("⚠️ 推送失败：", e)

def main():
    ensure_dirs()
    excel_ts = get_excel_timestamp()
    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)

    last_ts = state.get("excel_mtime", 0)

    if excel_ts <= last_ts:
        print("✅ Excel 未变化，无需更新。")
        return

    print("🔄 检测到 Excel 更新，正在重新生成配置...")

    rows = load_excel()
    for r in rows:
        write_proxy_yaml(r["id"], r["ip"], r["port"], r["user"], r["pwd"])
        stash_path = write_stash_yaml(r["id"])
        qr_path, url = make_qr(r["id"])
        print(f"✅ 生成 Phone{r['id']}：{url}\n📄 {stash_path}\n🧾 {qr_path}\n")

    git_push()
    state["excel_mtime"] = excel_ts
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f)

    print("🎉 已完成全部生成与推送。")

if __name__ == "__main__":
    main()
