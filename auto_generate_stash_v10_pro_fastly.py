import os, time, zipfile, qrcode, pandas as pd
from git import Repo
from pathlib import Path

# === 配置 ===
REPO_PATH = os.path.abspath(".")
OUTPUT_DIR = os.path.join(REPO_PATH, "output")
BACKUP_DIR = os.path.join(REPO_PATH, "backups")
EXCEL_FILE = os.path.join(REPO_PATH, "手机IP列表.xlsx")
GITHUB_REPO = "https://github.com/fashi88899/stash-config-FS.git"
CDN_BASE = "https://fastly.jsdelivr.net/gh/fashi88899/stash-config-FS@main/output"

def ensure_dirs():
    for p in [OUTPUT_DIR, BACKUP_DIR]:
        Path(p).mkdir(parents=True, exist_ok=True)

def backup_output():
    if not os.listdir(OUTPUT_DIR): return
    ts = time.strftime("%Y%m%d%H%M%S")
    zip_path = os.path.join(BACKUP_DIR, f"output_{ts}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(OUTPUT_DIR):
            for f in files:
                zf.write(os.path.join(root, f),
                         os.path.relpath(os.path.join(root, f), OUTPUT_DIR))
    print(f"💾 已备份上次输出：{zip_path}")

def load_excel():
    df = pd.read_excel(EXCEL_FILE)
    need_cols = ["手机编号","IP","端口","用户名","密码"]
    for c in need_cols:
        if c not in df.columns:
            raise SystemExit(f"Excel 缺少列：{c}")
    return df.to_dict("records")

def make_yaml(idx, ip, port, user, pwd):
    yaml = f"""mode: Rule
log-level: info
allow-lan: true
proxies:
- name: Phone{idx}
  type: socks5
  server: {ip}
  port: {port}
  username: {user}
  password: {pwd}
  udp: false
  ip-version: 4
  tls: false
  skip-cert-verify: true
proxy-groups:
- name: Proxy
  type: select
  proxies:
    - Phone{idx}
rules:
- DOMAIN-SUFFIX,whatsapp.net,Proxy
- DOMAIN-SUFFIX,whatsapp.com,Proxy
- IP-CIDR,31.13.64.0/18,Proxy
- MATCH,Proxy
"""
    return yaml

def make_qr(url, idx, ts):
    qr_path = os.path.join(OUTPUT_DIR, f"QR_Phone{idx}_{ts}.png")
    img = qrcode.make(url)
    img.save(qr_path)
    return qr_path

def git_push():
    try:
        repo = Repo(REPO_PATH)
        repo.git.add(A=True)
        repo.index.commit(f"Auto update (v10_fastly)")
        origin = repo.remote(name="origin")
        origin.push("main", force=True)
        print("🚀 Git 推送完成。")
    except Exception as e:
        print(f"⚠️ Git 推送失败: {e}")

def main():
    ensure_dirs()
    backup_output()
    rows = load_excel()
    ts = time.strftime("%Y%m%d%H%M%S")

    for r in rows:
        idx, ip, port, user, pwd = r["手机编号"], r["IP"], r["端口"], r["用户名"], r["密码"]
        yaml = make_yaml(idx, ip, port, user, pwd)
        yaml_path = os.path.join(OUTPUT_DIR, f"stash_{idx}.yaml")
        with open(yaml_path, "w", encoding="utf-8") as f:
            f.write(yaml)
        cdn_url = f"{CDN_BASE}/stash_{idx}.yaml?v={ts}"
        qr_path = make_qr(cdn_url, idx, ts)
        print(f"✅ 生成 Phone{idx}：{cdn_url}")
        print(f"📄 {yaml_path}")
        print(f"🧾 {qr_path}\n")

    git_push()
    print("\n🎉 全部节点已生成并推送。")

if __name__ == "__main__":
    main()
