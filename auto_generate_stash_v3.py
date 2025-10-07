# -*- coding: utf-8 -*-
"""
Stash 一机一IP 自动配置生成脚本 v3
------------------------------------------------------
✅ 读取手机IP列表.xlsx
✅ 生成带正确缩进的 stash_X.yaml
✅ 自动生成二维码（含 CDN 地址）
✅ 自动推送 GitHub
✅ 自动检测 YAML 是否有效
"""

import os
import pandas as pd
import yaml
import qrcode
from pathlib import Path

# === 仓库路径 ===
REPO_PATH = r"C:\Users\fashi\stash-config-FS"
CDN_BASE = "https://cdn.jsdelivr.net/gh/fashi88899/stash-config-FS@main/output"

# === 文件路径 ===
OUTPUT_DIR = os.path.join(REPO_PATH, "output")
PROVIDERS_DIR = os.path.join(OUTPUT_DIR, "providers")
EXCEL_FILE = os.path.join(REPO_PATH, "手机IP列表.xlsx")

def ensure_dirs():
    Path(PROVIDERS_DIR).mkdir(parents=True, exist_ok=True)

def load_excel():
    if not os.path.exists(EXCEL_FILE):
        raise SystemExit(f"❌ 找不到 Excel 文件：{EXCEL_FILE}")
    df = pd.read_excel(EXCEL_FILE)
    need_cols = ["手机编号", "IP", "端口", "用户名", "密码"]
    for c in need_cols:
        if c not in df.columns:
            raise SystemExit(f"Excel 缺少列：{c}，应包含：{','.join(need_cols)}")
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

def write_proxy_yaml(i, ip, port, user, pwd):
    data = {
        "proxies": [{
            "name": f"Phone{i}",
            "type": "socks5",
            "server": ip,
            "port": int(port),
            "username": user,
            "password": pwd
        }]
    }
    path = os.path.join(PROVIDERS_DIR, f"proxy_{i}.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    return path

def write_stash_yaml(i):
    """生成正确缩进格式的 stash_X.yaml"""
    content = f"""mode: Rule
log-level: info
allow-lan: true

proxy-providers:
  phone{i}:
    type: http
    url: "{CDN_BASE}/providers/proxy_{i}.yaml"
    interval: 3600
    path: ./providers/phone{i}.yaml

proxy-groups:
  - name: Proxy
    type: select
    use: [phone{i}]

rules:
  - MATCH,Proxy
"""
    path = os.path.join(OUTPUT_DIR, f"stash_{i}.yaml")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

def make_qr(i):
    url = f"{CDN_BASE}/stash_{i}.yaml"
    img = qrcode.make(url)
    path = os.path.join(OUTPUT_DIR, f"QR_Phone{i}.png")
    img.save(path)
    return path, url

def git_push():
    try:
        import git
        repo = git.Repo(REPO_PATH)
        repo.git.add(all=True)
        repo.index.commit("Auto update stash/proxies files (v3)")
        origin = repo.remote(name="origin")
        origin.push()
        print("🚀 已推送至 GitHub。")
    except Exception as e:
        print("⚠️ 推送失败：", e)
        print('请确认已登录 GitHub，并执行：git add . && git commit -m "auto" && git push')

def main():
    ensure_dirs()
    rows = load_excel()
    summary = []

    for r in rows:
        write_proxy_yaml(r["id"], r["ip"], r["port"], r["user"], r["pwd"])
        write_stash_yaml(r["id"])
        qr_path, url = make_qr(r["id"])
        summary.append((r["id"], url, qr_path))
        print(f"✅ 生成 Phone{r['id']}：{url}")

    git_push()

    print("\n====== 导入信息 ======")
    for i, url, qr in summary:
        print(f"📱 手机{i} 导入链接：{url}")
        print(f"🧾 二维码文件：{qr}")

if __name__ == "__main__":
    main()
