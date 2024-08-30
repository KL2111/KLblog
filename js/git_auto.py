import os
import subprocess
import datetime
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'git_auto_config.json')

def load_config():
    """加载已保存的配置文件"""
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_config(config):
    """保存配置到文件"""
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False)

def choose_directory():
    """选择Git仓库目录"""
    current_path = os.path.dirname(os.path.realpath(__file__))
    options = [
        current_path,
        os.path.dirname(current_path),
        os.path.dirname(os.path.dirname(current_path)),
        os.path.dirname(os.path.dirname(os.path.dirname(current_path)))
    ]
    for i, path in enumerate(options):
        print(f"{chr(65+i)}) {os.path.basename(path)}")
    choice = input("请选择仓库目录 (A-D) 或 N 退出: ").upper()
    if choice == 'N':
        print("程序已退出。")
        exit(0)
    elif choice in ['A', 'B', 'C', 'D']:
        index = ord(choice) - 65
        return options[index]
    else:
        print("无效的输入，重新选择。")
        return choose_directory()

def setup_remote_repo():
    """设置远程仓库地址"""
    remote_url = input("请输入SSH格式的远程仓库地址: ")
    if remote_url.startswith("git@"):
        return remote_url
    else:
        print("远程仓库地址格式错误，必须是SSH格式。")
        return setup_remote_repo()

def verify_ssh():
    """验证SSH公钥登录"""
    result = subprocess.run("ssh -T git@github.com", shell=True, text=True, capture_output=True)
    if "successfully authenticated" not in result.stderr:
        print("SSH公钥验证失败，请确保你的公钥已经添加到远程仓库。")
        exit(0)

def update_remote_repo(repo_dir, remote_url):
    """更新远程仓库地址"""
    os.chdir(repo_dir)
    print(f"Updating remote repository URL to {remote_url}")
    subprocess.run("git remote remove origin", shell=True, capture_output=True, text=True)
    subprocess.run(f"git remote add origin {remote_url}", shell=True, capture_output=True, text=True)

def commit_local_changes():
    """提交本地更改"""
    subprocess.run("git add -A", shell=True)
    commit_message = f"Local changes on {datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    subprocess.run(f"git commit -m '{commit_message}'", shell=True, capture_output=True, text=True)

def check_local_changes():
    """检查本地是否有未提交的更改"""
    status_result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    return status_result.stdout.strip() != ""

def is_git_repository(repo_dir):
    """检查是否是Git仓库"""
    return os.path.exists(os.path.join(repo_dir, '.git'))

def ensure_git_repo(repo_dir):
    """确保当前目录是一个 Git 仓库"""
    os.chdir(repo_dir)
    if not os.path.exists(os.path.join(repo_dir, '.git')):
        print("当前目录不是一个 Git 仓库，正在初始化...")
        subprocess.run("git init", shell=True)
        subprocess.run("touch README.md", shell=True)
        subprocess.run("git add README.md", shell=True)
        subprocess.run("git commit -m 'Initial commit'", shell=True)
        update_remote_repo(repo_dir, setup_remote_repo())
    else:
        print("当前目录已经是一个 Git 仓库。")

def handle_unfinished_rebase(repo_dir):
    """处理未完成的rebase操作"""
    if not is_git_repository(repo_dir):
        print("当前目录不是一个Git仓库，无法处理rebase操作。")
        exit(1)
    
    os.chdir(repo_dir)  # 确保切换到Git仓库目录
    
    rebase_dir = os.path.join(repo_dir, '.git', 'rebase-merge')
    if os.path.exists(rebase_dir):
        user_choice = input("检测到未完成的rebase操作。是否继续？(Y) 还是中止？(N) 还是放弃rebase并重新开始？(A): ").upper()
        if user_choice == 'Y':
            result = subprocess.run("git rebase --continue", shell=True, text=True, capture_output=True)
            if result.returncode != 0:
                print("尝试继续rebase操作时出错。")
                if result.stderr and "You must edit all merge conflicts" in result.stderr:
                    print("检测到冲突，仍然需要手动解决并添加已解决的文件。")
                else:
                    print(f"错误信息: {result.stderr}")
                exit(1)
            print("尝试继续rebase操作。")
            if os.path.exists(rebase_dir):
                print("rebase未完成，可能需要手动解决冲突。")
                exit(1)
            else:
                print("rebase操作已成功完成。")
        elif user_choice == 'N':
            subprocess.run("git rebase --abort", shell=True)
            print("未完成的rebase操作已中止。")
        elif user_choice == 'A':
            print("放弃当前的rebase操作，重新开始Git操作。")
            subprocess.run("git rebase --abort", shell=True)
            clean_git_lock(repo_dir)
            pull_and_update(repo_dir)
        else:
            print("无效选择。")
            exit(1)

def clean_git_lock(repo_dir):
    """清理遗留的git锁文件"""
    lock_file = os.path.join(repo_dir, '.git', 'index.lock')
    if os.path.exists(lock_file):
        print("检测到遗留的Git锁文件，正在清理...")
        os.remove(lock_file)

def check_for_git_processes():
    """检查是否有其他Git进程在运行"""
    result = subprocess.run("ps aux | grep '[g]it ' | grep -v 'Clash Verge' | grep -v 'WeChat' | grep -v 'Python'", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print("Detected the following Git-related processes:")
        print(result.stdout)
        choice = input("这些进程已被检测到。你要忽略并继续吗？(Y/N): ").upper()
        if choice == 'Y':
            print("继续脚本执行...")
        else:
            print("请终止这些进程后再继续。")
            exit(0)

def pull_and_update(repo_dir):
    """拉取最新更新并处理合并策略"""
    os.chdir(repo_dir)
    print(f"Pulling latest changes from origin")
    pull_result = subprocess.run("git pull origin master --allow-unrelated-histories", shell=True, text=True, capture_output=True)
    if pull_result.returncode != 0:
        print(f"拉取失败，错误信息: {pull_result.stderr}")
        handle_unfinished_rebase(repo_dir)
    else:
        print("Git操作完成。")

def merge_and_push(repo_dir):
    """合并并推送"""
    os.chdir(repo_dir)
    print(f"Pulling latest changes from origin")
    pull_result = subprocess.run("git pull --rebase origin master", shell=True, text=True, capture_output=True)
    if pull_result.returncode != 0:
        print(f"拉取失败，错误信息: {pull_result.stderr}")
        handle_unfinished_rebase(repo_dir)
        return
    
    commit_message = f"Commit after merging on {datetime.datetime.now().strftime('%Y%m%d')}"
    subprocess.run(f"git commit -m '{commit_message}'", shell=True, capture_output=True, text=True)
    
    push_result = subprocess.run("git push origin master", shell=True, text=True, capture_output=True)
    if push_result.returncode != 0:
        print(f"推送失败，错误信息: {push_result.stderr}")
        handle_unfinished_rebase(repo_dir)
    else:
        print("Git操作完成。")

def main():
    config = load_config()
    if config:
        use_existing = input("检测到已存在配置，是否使用此配置？首次使用一定要选择N重新配置(Y/N): ").upper()
        if use_existing == 'N':
            config = None

    if not config:
        print("首次运行配置程序。")
        repo_dir = choose_directory()
        remote_url = setup_remote_repo()
        save_config({'repo_dir': repo_dir, 'remote_url': remote_url})
    else:
        repo_dir = config['repo_dir']
        remote_url = config['remote_url']
    
    verify_ssh()
    ensure_git_repo(repo_dir)
    handle_unfinished_rebase(repo_dir)
    update_remote_repo(repo_dir, remote_url)
    
    if check_local_changes():
        commit_local_changes()

    merge_and_push(repo_dir)

if __name__ == "__main__":
    main()
