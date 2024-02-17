# 读取test.ass，以文本形式输出
import re
# 导入tk，用于弹出多选框进行选择
import tkinter as tk
from tkinter import filedialog

import chardet

from log_and_terdisp import log_message

Log2File = False
LogPrint = True


def is_chinese(content):
    return all(u'\u4e00' <= c <= u'\u9fff' for c in content)


def read_ass(path):
    encoder = chardet.detect(open(path, 'rb').read())['encoding']
    log_message("info", "文件编码为：" + encoder, Is2File=Log2File, IsPrint=LogPrint)
    with open(path, "r", encoding=encoder) as f:
        # 将整个文件一次性读取到变量ass中
        ass = f.read()
        f.close()
    return ass


def get_subtitles(ass):
    # 定位到字幕开始的内容，其标志我单独行的[Events]之下的内容
    start_index = ass.find('\n\n[Events]')
    # 提取字幕
    try:
        subtitles = ass[start_index:]
        head = ass[:start_index]
        log_message("info", "读取成功", Is2File=Log2File, IsPrint=LogPrint)
    except:
        # 如果找不到标志，则抛出异常，提示为：这可能不是一个有效的ASS文件，请用aegisub检查保存情况
        error = "这可能不是一个有效的ASS文件，请用aegisub检查保存情况"
        log_message("error", error, Is2File=Log2File, IsPrint=LogPrint)
        raise Exception(error)

    return subtitles, head


def segment_subs_2_dict(subtitles):
    subtitles = subtitles.replace('[Events]', '')
    # 将字幕内容按行分割
    lines = subtitles.split('\n')
    # 输出有多少行
    log_message("info", "字幕行数：" + str(len(lines)), Is2File=Log2File, IsPrint=LogPrint)
    # 将每一行的内容按照:分割
    new_lines = []
    count = 0
    for i in lines:
        # 查找第一个冒号的位置
        index = i.find(':')
        if i[:index] == '' and i[index + 1:] == '':
            continue
        # 按照第一个冒号分割
        new_lines.append([])
        new_lines[count].append(i[:index])
        new_lines[count].append(i[index + 1:])
        count += 1
    # 输出分割后的内容
    log_message("info", "分割后的内容：" + str(new_lines), Is2File=Log2File, IsPrint=False)
    return new_lines


def count_all_names(new_lines):
    # 遍历new_lines每一行的第二项，查找其中形如[James]的内容，将这些记录到一个字典中，并统计其出现的次数
    name_count = {}
    count = 0
    for i in new_lines:
        strs = i[1]
        # 用正则表达式匹配形如[James]的内容
        pattern = r'\[(.*?)\]'
        matches = re.findall(pattern, strs)

        for j in range(len(matches)):
            if len(matches[j]) == 0:
                continue
            # print(matches[j])
            # 判断是不是中文，如果是中文则剔除
            if is_chinese(matches[j]) or ' ' in matches[j] or not matches[j][0].isupper():
                matches.remove(matches[j])
        # print(matches)
        # 取出matches中的内容并记录到字典name_count中，统计其出现的次数
        if len(matches) == 0:
            count += 1
            continue
        for j in matches:
            if j not in name_count:
                name_count[j] = 1
            else:
                name_count[j] += 1
    log_message("info", "出现的人名为：：" + str(name_count), Is2File=Log2File, IsPrint=LogPrint)
    return name_count


def replace_name(name, subtitles):
    # 遍历subtitle，将[name]的字符删除
    for i in subtitles:
        i[1] = i[1].replace(f'[{name}]', '')
    log_message('info', f'替换完成：{name}', Is2File=Log2File, IsPrint=LogPrint)
    return subtitles


def multi_selector(name_count):
    def get_selected():
        # 获取选择内容
        # 将name_selected设置为全局变量
        global name_selected
        name_selected = []
        for i in lb.curselection():
            name_selected.append(lb.get(i))
        log_message("info", "选择替换的人名为：：" + str(name_selected), Is2File=Log2File, IsPrint=LogPrint)
        # 退出窗口
        root.quit()

    root = tk.Tk()
    root.title('请选择需要替换的人名')
    # 创建一个列表
    lb = tk.Listbox(root, selectmode=tk.MULTIPLE)
    lb.pack()
    # 为列表添加内容
    for i in name_count.keys():
        lb.insert(tk.END, i)
    # 创建一个按钮，点击按钮后获取选择的内容
    btn = tk.Button(root, text='获取选择的内容', command=get_selected)
    btn.pack()
    # 设置显示窗口的位置为屏幕中央
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
    root.geometry("+%d+%d" % (x, y))
    # 显示窗口
    root.mainloop()


def file_selector():
    # 用tk创建文件选择窗口，用于选择ass字幕文件
    root = tk.Tk()
    root.withdraw()
    file_path = tk.filedialog.askopenfilename()
    return file_path


def replace_punctuation(subtitles):
    # 遍历subtitle，将中文标点替换为空格
    for i in subtitles:
        i[1] = i[1].replace('，', ' ')
        i[1] = i[1].replace('。', ' ')
        i[1] = i[1].replace('、', ' ')
        i[1] = i[1].replace('；', ' ')
        i[1] = i[1].replace('……', '…')
    log_message('info', f'中文标点替换完成', Is2File=Log2File, IsPrint=LogPrint)
    return subtitles


def output_subs(subtitles, head, output_path):
    # ass文件的头部
    head = head
    # 重组字幕
    new_subs = ''
    for i in subtitles:
        new_subs += i[0] + ':' + i[1] + '\n'
    # 输出到文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(head + "\n\n[Events]\n" + new_subs)
        f.close()
    log_message('info', f'新的字幕文件已经输出到：{output_path}', Is2File=Log2File, IsPrint=LogPrint)


if __name__ == '__main__':
    # path = 'test.ass'
    input_path = file_selector()
    output_path = input_path.replace('.ass', '_new.ass')
    ass = read_ass(input_path)
    subtitles, head = get_subtitles(ass)
    # 分割字幕为列表
    subtitles = segment_subs_2_dict(subtitles)
    # 统计所有人名和每个人名出现的次数
    name_count = count_all_names(subtitles)
    # 弹出一个多选框，根据name_count选择需要替换的人名
    multi_selector(name_count)
    # 替换人名
    for name in name_selected:
        subtitles = replace_name(name, subtitles)
    # 替换字幕中出现的中文符号
    subtitles = replace_punctuation(subtitles)
    # 将字幕重组，并输出
    output_subs(subtitles, head, output_path)
