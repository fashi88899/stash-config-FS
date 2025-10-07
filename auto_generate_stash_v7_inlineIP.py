# -*- coding: utf-8 -*-
import os, pandas as pd, yaml, qrcode, json, subprocess
from pathlib import Path

REPO_PATH = r"C:\Users\fashi\stash-config-FS"
CDN_BASE  = "https://cdn.jsdelivr.net/gh/fashi88899/stash-config-FS@main/output"

OUTPUT_DIR    = os.path.join(REPO_PATH, "output")
EXCEL_FILE    = os.path.join(REPO_PATH, "手机IP列表.xlsx")
STATE_FILE    = os.path.join(REPO_PATH, ".last_update_inline.json")

def ensure_dirs():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def excel_mtime():
    return int(os.path.getmtime(EXCEL_FILE)) if os.path.exists(EXCEL_FILE) else 0

def load_rows():
    df = pd.read_excel(EXCEL_FILE)
    need = ["手机编号","IP","端口","用户名","密码"]
    for c in need:
        if c not in df.columns:
            raise SystemExit(f"Excel 缺少列：{c}（需要：{','.join(need)}）")
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
        import yaml
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, indent=2, default_flow_style=False)
    return path

def make_qr(i):
    url = f"{CDN_BASE}/stash_{i}.yaml"
    img = qrcode.make(url)
    path = os.path.join(OUTPUT_DIR, f"QR_Phone{i}.png")
    img.save(path)
    return path, url

def auto_push():
    try:
        subprocess.run(["git", "add", "."], cwd=REPO_PATH, check=False)
        subprocess.run(["git", "commit", "-m", "Auto update (v7 inlineIP)"], cwd=REPO_PATH, check=False)
        subprocess.run(["git", "push"], cwd=REPO_PATH, check=False)
        print("🚀 已自动推送至 GitHub。")
    except Exception as e:
        print("⚠️ 推送失败：", e)

def main():
    ensure_dirs()
    rows = load_rows()
    for r in rows:
        p = write_stash_inline(r["id"], r["ip"], r["port"], r["user"], r["pwd"])
        qr, url = make_qr(r["id"])
        print(f"✅ 生成 Phone{r['id']}：{url}\n📄 {p}\n🧾 {qr}\n")
    auto_push()

if __name__ == "__main__":
    main()
