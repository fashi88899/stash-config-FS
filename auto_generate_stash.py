# -*- coding: utf-8 -*-
import os, pandas as pd, yaml, qrcode
from pathlib import Path

# ===== 用户可改区域 =====
REPO_PATH = r"C:\Users\fashi\stash-config-FS"   # 你的仓库本地路径
CDN_BASE  = "https://cdn.jsdelivr.net/gh/fashi88899/stash-config-FS@main"             # 生成的线上链接前缀（jsDelivr）
# =======================

OUTPUT_DIR    = os.path.join(REPO_PATH, "output")
PROVIDERS_DIR = os.path.join(OUTPUT_DIR, "providers")
EXCEL_FILE    = os.path.join(REPO_PATH, "手机IP列表.xlsx")

def ensure_dirs():
    Path(PROVIDERS_DIR).mkdir(parents=True, exist_ok=True)

def load_rows():
    if not os.path.exists(EXCEL_FILE):
        raise SystemExit("找不到 Excel：%s" % EXCEL_FILE)
    df = pd.read_excel(EXCEL_FILE)
    need_cols = ["手机编号","IP","端口","用户名","密码"]
    for c in need_cols:
        if c not in df.columns:
            raise SystemExit("Excel 缺少列：%s（应包含：%s）" % (c, ",".join(need_cols)))
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
        "proxies": [{"name": f"Phone{i}","type":"socks5","server": ip,"port": int(port),
                    "username": user, "password": pwd}]
    }
    path = os.path.join(PROVIDERS_DIR, f"proxy_{i}.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    return path

def write_stash_yaml(i):
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
    url = f"{CDN_BASE}/stash_{i}.yaml"
    img = qrcode.make(url)
    path = os.path.join(OUTPUT_DIR, f"QR_Phone{i}.png")
    img.save(path)
    return path, url

def git_push():
    try:
        import git
    except ImportError:
        print("⚠️ 未安装 GitPython：执行 pip install gitpython 后可自动推送。当前仅生成文件，不推送。")
        return False
    try:
        repo = git.Repo(REPO_PATH)
        repo.git.add(all=True)
        repo.index.commit("Auto update stash/proxies files")
        origin = repo.remote(name='origin')
        origin.push()
        print("🚀 已推送到 GitHub。")
        return True
    except Exception as e:
        print("⚠️ 推送失败：", e)
        print('请确认已登录 GitHub，并在该仓库目录手动执行：git add . && git commit -m "auto" && git push')
        return False

def main():
    ensure_dirs()
    rows = load_rows()
    summary = []
    for r in rows:
        p1 = write_proxy_yaml(r["id"], r["ip"], r["port"], r["user"], r["pwd"])
        p2 = write_stash_yaml(r["id"])
        qrp, url = make_qr(r["id"])
        summary.append((r["id"], url, qrp))
        print(f"✅ 生成 Phone{r['id']} → {url}  ｜ QR: {os.path.basename(qrp)}")
    pushed = git_push()
    print("\n====== 导入信息 ======")
    for i, url, qrp in summary:
        print(f"Phone{i}: {url}  ｜ QR: {qrp}")
    if not pushed:
        print("\n提示：未自动推送成功，可在仓库目录手动 push。")

if __name__ == "__main__":
    main()