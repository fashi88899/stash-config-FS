# -*- coding: utf-8 -*-
"""
Stash 一机一IP 自动配置生成脚本 v2
------------------------------------------------------
功能：
✅ 从 Excel 自动读取手机编号、IP、端口、账号密码
✅ 自动生成每台手机的 YAML 配置文件（在 /output/ 下）
✅ 自动生成二维码（可扫码导入）
✅ 自动推送到 GitHub 仓库
✅ 控制台输出每台手机的导入链接（CDN路径）

作者: 师法
"""

import os
import pandas as pd
import yaml
import qrcode
from pathlib import Path

# === 你的仓库路径（请保持一致） ===
REPO_PATH = r"C:\Users\fashi\stash-config-FS"
CDN_BASE = "https://cdn.jsdelivr.net/gh/fashi88899/stash-config-FS@main/output"

# === 路径设定 ===
OUTPUT_DIR = os.path.join(REPO_PATH, "output")
PROVIDERS_DIR = os.path.join(OUTPUT_DIR, "providers")
EXCEL_FILE = os.path.join(REPO_PATH, "手机IP列表.xlsx")

def ensure_dirs():
    Path(PROVIDERS_DIR).mkdir(parents=True, exist_ok=True)

def load_excel():
    if not os.path.exists(EXCEL_FILE):
        raise SystemExit(f"❌ 找不到 Excel 文件：{EXCEL_FILE}")
    df = pd.read_excel(EXCEL_FILE)
    need_cols = ["手机编号","IP","端口","用户名","密码"]
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
    """生成 output/stash_X.yaml"""
    content = f"""
    mode: Rule
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
        f.write("\n".join([ln.strip() for ln in content.strip().splitlines()]) + "\n")
    return path

def make_qr(i):
    """生成二维码"""
    url = f"{CDN_BASE}/stash_{i}.yaml"
    img = qrcode.make(url)
    path = os.path.join(OUTPUT_DIR, f"QR_Phone{i}.png")
    img.save(path)
    return path, url

def git_push():
    """自动 git 提交并推送"""
    try:
        import git
    except ImportError:
        print("⚠️ 未安装 GitPython：请执行 pip install gitpython 后再试。")
        return False
    try:
        repo = git.Repo(REPO_PATH)
        repo.git.add(all=True)
        repo.index.commit("Auto update stash/proxies files (v2)")
        origin = repo.remote(name="origin")
        origin.push()
        print("🚀 已推送至 GitHub。")
        return True
    except Exception as e:
        print("⚠️ 推送失败：", e)
        print('请确认已登录 GitHub，并在仓库目录执行：git add . && git commit -m "auto" && git push')
        return False

def main():
    ensure_dirs()
    rows = load_excel()
    summary = []
    for r in rows:
        write_proxy_yaml(r["id"], r["ip"], r["port"], r["user"], r["pwd"])
        write_stash_yaml(r["id"])
        qr_path, url = make_qr(r["id"])
        summary.append((r["id"], url, qr_path))
        print(f"✅ 生成 Phone{r['id']}：{url} ｜ 二维码：{os.path.basename(qr_path)}")

    pushed = git_push()

    print("\n====== 导入信息 ======")
    for i, url, qr in summary:
        print(f"📱 手机{i} 导入链接：{url}")
        print(f"🧾 二维码文件：{qr}")
    if not pushed:
        print("\n⚠️ 文件已生成，但未成功推送，可手动 push 一次。")

if __name__ == "__main__":
    main()
