import os
import sys
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def find_recent_files(root_dir, max_days=3):
    current_time = time.time()
    seconds_limit = max_days * 24 * 3600
    
    print(f"Searching in {root_dir}...")
    found_files = []
    
    # We will search up to depth 4 to be fast
    for root, dirs, files in os.walk(root_dir):
        # Limit recursion depth for very large folders
        depth = root[len(root_dir):].count(os.sep)
        if depth > 4:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            try:
                mtime = os.path.getmtime(file_path)
                if current_time - mtime < seconds_limit:
                    if "장미" in file or "2-1" in file or "학습" in file or "만화" in file:
                        found_files.append((file_path, mtime))
            except Exception as e:
                pass
                
    found_files.sort(key=lambda x: x[1], reverse=True)
    for path, mtime in found_files:
        local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
        print(f"{local_time} - {path}")

if __name__ == "__main__":
    find_recent_files("C:/Users/roadsea")
    find_recent_files("J:/홈페이지")
