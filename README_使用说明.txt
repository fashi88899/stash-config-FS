📘 Stash 自动配置脚本使用说明（v10_fastly）
一、环境准备

安装 Python 3.11+
👉 https://www.python.org/downloads/

安装 Git
👉 https://git-scm.com/downloads

打开命令提示符 (CMD)
输入：

pip install pandas qrcode gitpython openpyxl


（等待全部安装成功）
二、文件结构
stash-config-FS/
 ├─ auto_generate_stash_v10_pro_fastly.py
 ├─ 手机IP列表.xlsx
 ├─ README_使用说明.txt
 ├─ /output/
 └─ /backups/

三、Excel 表填写规范

打开 手机IP列表.xlsx：

手机编号	IP	端口	用户名	密码
1	38.213.193.104	6051	Fs_UK1	ab123456
2	91.149.251.116	10324	Fs_UK1	ab123456

⚠️ 注意：

所有列名必须与上方完全一致（中英文不能混）；

“端口”必须为纯数字；

文件路径与脚本保持在同一文件夹。

四、运行脚本

打开 CMD
切换到脚本所在目录：

cd C:\Users\fashi\stash-config-FS


运行：

python auto_generate_stash_v10_pro_fastly.py


运行后会自动：

生成配置文件：stash_1.yaml / stash_2.yaml

自动上传 GitHub 仓库

自动生成二维码图片 QR_Phone1_xxx.png

五、扫码导入 Stash

打开手机 Stash → Configurations → + → Scan QR

扫描生成的二维码（在 /output/ 文件夹）

自动导入链接示例：

https://fastly.jsdelivr.net/gh/fashi88899/stash-config-FS@main/output/stash_1.yaml?v=20251009xxxx


导入后，点击「Test」确认节点是否可连接 ✅

六、Git 推送成功标识

运行日志若显示：

🚀 Git 推送完成。
✅ 生成 Phone1：https://fastly.jsdelivr.net/...


说明同步成功。

刷新仓库页面：
👉 https://github.com/fashi88899/stash-config-FS

即可看到文件更新。

七、常见问题（FAQ）
问题	解决方案
⚠️ 导入失败	重新生成配置或清除 CDN 缓存：访问链接尾部加 ?v=当前时间戳
⚠️ IP 未更新	删除旧配置文件 → 扫描最新二维码
⚠️ Stash 无法连接	检查 IP/端口 是否有效、UDP 是否关闭
⚠️ Git 推送报错	执行命令：git pull origin main --rebase 再重试
⚠️ YAML 显示无效	确保缩进为 2 空格格式；不要混用 tab
八、示意截图（推荐放在 README 同目录）

可在运行后截图：

CMD 控制台生成日志

GitHub 页面更新文件

手机端扫码导入成功页面

✅ 完成！
现在你只需修改 Excel 内的 IP、端口、账号信息，再运行脚本即可自动生成并同步所有配置