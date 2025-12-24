# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import codecs
import subprocess

def to_unicode(s):
    """兼容Python2/3的字符串编码处理"""
    if sys.version_info[0] == 2:
        if isinstance(s, str):
            return s.decode(sys.getfilesystemencoding() or 'utf-8')
        return s
    else:
        return str(s)

def setup_windows_console():
    """Windows系统自动切换控制台编码为GBK（避免中文乱码），其他系统跳过"""
    if sys.platform.startswith('win32'):
        try:
            # 执行 chcp 936 切换编码，隐藏命令行输出（stdout/stderr重定向到DEVNULL）
            devnull = open(os.devnull, 'w') if sys.version_info[0] == 2 else subprocess.DEVNULL
            subprocess.call('chcp 936 >nul 2>&1', shell=True, stdout=devnull, stderr=devnull)
            if sys.version_info[0] == 2:
                devnull.close()
        except Exception as e:
            # 切换失败不中断脚本，仅提示
            safe_print(u"ℹ️ Windows控制台编码切换失败（不影响功能，可能存在乱码）：{}".format(to_unicode(str(e))))

def safe_print(s):
    """兼容Python2/3的中文输出，配合控制台编码切换彻底解决乱码"""
    if sys.version_info[0] == 2:
        # Python2：强制GBK编码输出（匹配切换后的控制台编码）
        try:
            print(s.encode('gbk', errors='replace'))  # 无法编码的字符用“?”替代，避免报错
        except:
            print(s.encode('utf-8', errors='replace'))
    else:
        # Python3：直接打印（默认支持Unicode，配合Windows控制台GBK编码正常显示）
        print(s)

def main():
    # 第一步：自动配置Windows控制台编码（仅Windows生效）
    setup_windows_console()

    # 后续逻辑不变，保持原有功能
    current_dir = to_unicode(os.getcwd())
    safe_print(u"===== 开始执行子目录index.md索引生成脚本 =====")
    safe_print(u"当前检索根目录：{}".format(current_dir))
    safe_print(u"正在递归检索所有子文件夹...\n")

    index_links = []
    for root, dirs, files in os.walk(current_dir):
        root = to_unicode(root)
        files_unicode = [to_unicode(f) for f in files]
        if root == current_dir:
            continue
        if u"index.md" in files_unicode:
            relative_dir = to_unicode(os.path.relpath(root, current_dir))
            link_path = os.path.join(relative_dir, u"index.md").replace(os.sep, "/")
            link_text = relative_dir
            index_links.append( (link_text, link_path) )
            safe_print(u"找到索引文件：{} -> {}".format(link_text, link_path))

    current_index_path = to_unicode(os.path.join(current_dir, u"index.md"))
    safe_print(u"\n===== 开始生成/更新索引文件 =====")
    safe_print(u"目标索引文件：{}".format(current_index_path))

    try:
        with codecs.open(current_index_path, "w", encoding="utf-8") as f:
            f.write(u"# 子目录索引\n")
            f.write(u"> 本文件由脚本自动生成，包含所有子文件夹中的index.md链接\n")
            f.write(u"> 生成说明：跨平台兼容、支持中文路径、Python2/3双版本适配、自动解决乱码\n\n")
            if index_links:
                f.write(u"## 可用索引列表\n\n")
                for link_text, link_path in index_links:
                    f.write(u"- [{}]({})\n".format(link_text, link_path))
                safe_print(u"成功写入 {} 个索引链接".format(len(index_links)))
            else:
                f.write(u"## 可用索引列表\n\n")
                f.write(u"> 未找到任何子文件夹中的index.md文件\n")
                safe_print(u"未找到符合条件的index.md文件，已创建空索引文件")
    except Exception as e:
        safe_print(u"❌ 写入文件时出错：{}".format(to_unicode(str(e))))
        sys.exit(1)

    safe_print(u"\n===== 操作完成！=====")
    safe_print(u"提示：打开 {} 查看生成的索引".format(current_index_path))

if __name__ == "__main__":
    main()