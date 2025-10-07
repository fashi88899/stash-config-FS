使用说明 - auto_generate_stash_v8_final
====================================
1️⃣ 解压到：C:\Users\fashi\stash-config-FS\
2️⃣ 编辑 手机IP列表.xlsx（已预置两台手机）
3️⃣ 在命令行运行：
   cd C:\Users\fashi\stash-config-FS
   python auto_generate_stash_v8_final.py

脚本功能：
✅ 自动生成 output\stash_X.yaml（直写 IP）
✅ 自动生成二维码 QR_PhoneX.png
✅ 自动推送 GitHub 同步
✅ 输出每个手机的导入链接（带 ?v=时间戳 参数防缓存）

在 Stash App 导入：
打开 Configurations → ＋ → From URL
粘贴或扫码输出链接即可。
