
使用说明（Windows）
==================
1) 把本压缩包解压到：C:\Users\fashi\stash-config-FS
   其中 `auto_generate_stash.py` 与 `手机IP列表.xlsx` 放在仓库根目录。

2) 安装依赖（只需一次）：
   pip install pandas pyyaml qrcode[pil] gitpython openpyxl

3) 编辑 Excel：手机IP码。列表.xlsx
   按行填写：手机编号、IP、端口、用户名、密

4) 运行：
   cd C:\Users\fashi\stash-config-FS
   python auto_generate_stash.py

5) 运行结果：
   - 生成 output/ 下的 stash_X.yaml、providers/proxy_X.yaml、QR_PhoneX.png
   - 自动 git add/commit/push 推送到 GitHub
   - 终端会打印每台手机的导入链接（CDN 地址）

如推送失败，请先在仓库目录执行一次手动 push 完成登录：
   git add . && git commit -m "init" && git push
