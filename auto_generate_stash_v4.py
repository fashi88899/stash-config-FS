# -*- coding: utf-8 -*-
"""
Stash 一机一IP 自动配置系统 v4
------------------------------------------------------
✅ 自动读取 手机IP列表.xlsx
✅ 自动生成正确缩进的 stash_X.yaml
✅ 自动生成二维码 (CDN 链接)
✅ 自动推送 GitHub
✅ 自动验证 YAML 结构有效性
"""

import os
import pandas as pd
import yaml
import qrcode
from pathlib import Path

# === 仓库根路径（请改为你自己的路径） ===
REPO_PATH = r"C:\Users\fashi\stash-config-FS"
CDN_BASE = "https://cdn.jsdelivr.net/gh/fashi88899/stash-config-FS@main/output"

# === 文件路径 ===
OUTPUT_DIR = os.path.join(REPO_PATH, "output")
PROVIDERS_DIR = os.path.join(OUTPUT_DIR, "providers")
EXCEL_FILE = os.path.join(REPO_PATH, "手机IP列表.xlsx")

def ensure_dirs():
    Path(PROVIDERS_DIR).mkdir(parents=True, exist_ok=True)

def load_excel():
    """读取 Excel 数据"""
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
    """生成 providers/proxy_X.yaml"""
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
    data = {
        "mode": "Rule",
        "log-level": "info",
        "allow-lan": True,
        "proxy-providers": {
            f"phone{i}": {
                "type": "http",
                "url": f"{CDN_BASE}/providers/proxy_{i}.yaml",
                "interval": 3600,
                "path": f"./providers/phone{i}.yaml"
            }
        },
        "proxy-groups": [
            {"name": "Proxy", "type": "select", "use": [f"phone{i}"]}
        ],
        "rules": ["MATCH,Proxy"]
    }

    path = os.path.join(OUTPUT_DIR, f"stash_{i}.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    return path

def make_qr(i):
    """生成二维码"""
    url = f"{CDN_BASE}/stash_{i}.yaml"
    img = qrcode.make(url)
    path = os.path.join(OUTPUT_DIR, f"QR_Phone{i}.png")
    img.save(path)
    return path, url

def git_push():
    """自动推送到 GitHub"""
    try:
        import git
        repo = git.Repo(REPO_PATH)
        repo.git.add(all=True)
        repo.index.commit("Auto update stash/proxies files (v4)")
        origin = repo.remote(name="origin")
        origin.push()
        print("🚀 已推送至 GitHub。")
    except Exception as e:
        print("⚠️ 推送失败：", e)
        print('请确认已登录 GitHub，并执行：git add . && git commit -m "auto" && git push')

def validate_yaml(path):
    """验证生成的 YAML 文件是否格式正确"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            yaml.safe_load(f)
        return True
    except Exception as e:
        print(f"⚠️ YAML 验证失败 ({os.path.basename(path)}): {e}")
        return False

def main():
    ensure_dirs()
    rows = load_excel()
    summary = []

    for r in rows:
        write_proxy_yaml(r["id"], r["ip"], r["port"], r["user"], r["pwd"])
        stash_path = write_stash_yaml(r["id"])
        qr_path, url = make_qr(r["id"])
        is_valid = validate_yaml(stash_path)
        summary.append((r["id"], url, qr_path, is_valid))
        print(f"✅ 生成 Phone{r['id']}：{url}")

    git_push()

    print("\n====== 导入信息 ======")
    for i, url, qr, ok in summary:
        status = "✅ 格式正确" if ok else "⚠️ 格式异常"
        print(f"📱 手机{i} 导入链接：{url}  ｜ {status}")
        print(f"🧾 二维码文件：{qr}")

if __name__ == "__main__":
    main()
