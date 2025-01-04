import re
from datetime import datetime, timedelta
import sys

with open('logs.txt', 'r', encoding='utf-8', errors='replace') as file:
    logs = file.read()

pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \| \d{2}:\d{2}:\d{2}) \(EST\)\s+destiny:\s*(.*?)\s+Destinygg', re.DOTALL)
matches = pattern.findall(logs)

log_entries = []
for match in matches:
    timestamp = datetime.strptime(match[0], '%Y-%m-%d | %H:%M:%S')
    message = match[1].strip()
    log_entries.append((timestamp, message))

log_entries.sort(key=lambda x: x[0])
earliest_time = log_entries[0][0]
latest_time = log_entries[-1][0]


def seconds_to_srt_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{int(h):02}:{int(m):02}:{int(s):02},{ms:03}"


def print_progress_bar(iteration, total, length=50):
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r|{bar}| {percent}% Completed')
    sys.stdout.flush()
    if iteration == total:
        print()


srt_entries = []
index = 1


def create_srt_entry(index, start_time, end_time, logs):
    srt_texts = []
    for log in logs:
        srt_texts.append(f"{log[0].strftime('%Y-%m-%d | %H:%M:%S')} (EST)\n{log[1]}")
    return f"{index}\n{seconds_to_srt_time(start_time)} --> {seconds_to_srt_time(end_time)}\n" + "\n".join(srt_texts) + "\n\n"


start_time = 0
current_logs = []

for i in range(len(log_entries)):
    log = log_entries[i]
    log_time = (log[0] - earliest_time).total_seconds()
    next_log_time = (log_entries[i + 1][0] - earliest_time).total_seconds() if i + 1 < len(log_entries) else log_time + 20  # Assume 20 seconds after the last log
    time_diff = next_log_time - log_time

    current_logs.append(log)

    if time_diff >= 20 or len(current_logs) > 3:
        end_time = log_time if time_diff >= 20 else next_log_time
        srt_entries.append(create_srt_entry(index, start_time, end_time, current_logs))
        current_logs = [] if time_diff >= 20 else current_logs[-3:]
        start_time = log_time if time_diff >= 20 else end_time
        index += 1

    print_progress_bar(i + 1, len(log_entries))

if current_logs:
    srt_entries.append(create_srt_entry(index, start_time, (latest_time - earliest_time).total_seconds(), current_logs))

with open("logs_subtitles.srt", "w", encoding="utf-8") as srt_file:
    srt_file.writelines(srt_entries)
