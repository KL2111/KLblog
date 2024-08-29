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

def force_remote_overwrite():
    """强制远程覆盖本地"""
    subprocess.run("git fetch origin", shell=True)
    subprocess.run("git reset --hard origin/master", shell=True)
    print("远程仓库已覆盖本地仓库。")

def force_local_overwrite():
    """强制本地覆盖远程"""
    if check_local_changes():
        commit_local_changes()
    subprocess.run("git push origin master --force", shell=True)
    print("本地仓库已覆盖远程仓库。")

def merge_and_push(repo_dir):
    """合并并推送"""
    os.chdir(repo_dir)
    print(f"Pulling latest changes from origin")
    pull_result = subprocess.run("git pull --rebase origin master", shell=True, text=True, capture_output=True)
    if pull_result.returncode != 0:
        print(f"拉取失败，错误信息: {pull_result.stderr}")
        handle_merge_conflict()
        return
    # 获取用户的commit信息或使用默认日期作为commit信息
    commit_message = input("请输入commit信息（日期信息已默认输入）: ")
    if not commit_message:
        commit_message = datetime.datetime.now().strftime("%Y%m%d")
    else:
        commit_message = datetime.datetime.now().strftime("%Y%m%d_") + commit_message
    # 添加所有更改到staging area
    subprocess.run("git add -A", shell=True)
    # 执行commit，如果没有变化则不会创建新的commit
    commit_result = subprocess.run(f"git commit -m '{commit_message}'", shell=True, text=True, capture_output=True)
    if "nothing to commit" in commit_result.stdout or "nothing to commit" in commit_result.stderr:
        print("没有发现需要提交的更改。")
    else:
        print("Committing changes")
    # 推送更改到远程仓库
    push_result = subprocess.run("git push origin master", shell=True, text=True, capture_output=True)
    if push_result.returncode != 0:
        print(f"推送失败，错误信息: {push_result.stderr}")
        handle_merge_conflict()
    else:
        print("Git操作完成。")

def handle_merge_conflict():
    """处理合并冲突"""
    strategy = input("合并冲突，请选择冲突解决策略：1. 强制远程覆盖本地 2. 强制本地覆盖远程 3. 手动解决冲突 (1/2/3): ")
    if strategy == '1':
        confirmation = input("确定要强制远程覆盖本地吗？这将丢失本地所有未推送的更改 (Y/N): ").upper()
        if confirmation == 'Y':
            force_remote_overwrite()
        else:
            print("操作已取消。")
    elif strategy == '2':
        confirmation = input("确定要强制本地覆盖远程吗？这将丢失远程仓库中的所有更改 (Y/N): ").upper()
        if confirmation == 'Y':
            force_local_overwrite()
        else:
            print("操作已取消。")
    elif strategy == '3':
        print("请手动解决所有冲突并继续操作。")
        print("解决所有冲突后，运行以下命令完成rebase并推送：")
        print("git add <conflicted_files>")
        print("git rebase --continue")
        print("git push origin master")
    else:
        print("无效选择，退出程序。")

def clean_git_lock(repo_dir):
    """清理Git锁文件"""
    lock_file = os.path.join(repo_dir, '.git', 'index.lock')
    if os.path.exists(lock_file):
        os.remove(lock_file)
        print("Removed stale index.lock file.")

def check_for_git_processes():
    """检查是否有其他Git进程在运行"""
    result = subprocess.run("ps aux | grep '[g]it'", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print("Detected another Git process running. Please wait for it to complete or terminate it before proceeding.")
        exit(0)

def handle_unfinished_rebase(repo_dir):
    """处理未完成的rebase操作"""
    rebase_dir = os.path.join(repo_dir, '.git', 'rebase-merge')
    if os.path.exists(rebase_dir):
        user_choice = input("检测到未完成的rebase操作，是否中止操作？ (Y/N): ").upper()
        if user_choice == 'Y':
            subprocess.run("git rebase --abort", shell=True)
            print("未完成的rebase操作已中止。")
        else:
            print("请手动完成rebase操作后再运行此脚本。")
            exit(1)

def stash_local_changes():
    """暂存本地更改"""
    subprocess.run("git stash", shell=True)
    print("Stashed local changes.")

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
    clean_git_lock(repo_dir)
    # check_for_git_processes()  # 如果确认没有其他 Git 进程，可以暂时注释掉这行
    handle_unfinished_rebase(repo_dir)
    stash_local_changes()
    ensure_git_repo(repo_dir)
    update_remote_repo(repo_dir, remote_url)
    
    if check_local_changes():
        commit_local_changes()

    merge_and_push(repo_dir)

if __name__ == "__main__":
    main()
