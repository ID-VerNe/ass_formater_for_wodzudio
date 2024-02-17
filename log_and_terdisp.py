import time

from termcolor import colored


def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))


severity_levels = {'INPUT': 1, 'INFO': 2, 'WARNING': 3, 'ERROR': 4, 'REPLY': 2}


def log_message(level, content, min_level='INFO', Is2File=False, IsPrint=True):
    min_severity = severity_levels[min_level.upper()]
    log_severity = severity_levels[level.upper()]

    level = level.upper()
    content = str(content)

    if log_severity >= min_severity:
        level_colors = {'INFO': 'green', 'ERROR': 'red', 'WARNING': 'yellow', 'INPUT': 'blue', 'REPLY': 'cyan'}
        log_content = str(get_time()) + ' ' + colored(f'[{level}] ', level_colors[level]) + content
        if IsPrint:
            print(log_content)
        if Is2File:
            # 如果是reply，则不写入文件
            if level == 'REPLY':
                pass
            # 将log写入文件
            else:
                with open('log.txt', 'a', encoding='utf-8') as f:
                    f.write(log_content + '\n')
        else:
            pass

        return log_content
    else:
        return None


if __name__ == '__main__':
    print(log_message('info', '这是一条测试信息'))
