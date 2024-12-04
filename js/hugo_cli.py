import os
import subprocess

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
        print(f"{chr(65+i)}) {os.path.basename(path)} - {path}")
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

def run_hugo_server():
    """运行 hugo server"""
    print("正在启动 hugo server...")
    server_process = subprocess.Popen(["hugo", "server"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = server_process.communicate()
    print("Hugo Server 输出:", stdout.decode())
    if stderr:
        print("错误信息:", stderr.decode())
    try:
        input("Hugo server 已启动。按 Enter 停止并继续...")
    finally:
        server_process.terminate()
        server_process.wait()
        print("Hugo server 已停止。")

def ask_to_publish_site():
    """询问是否发布网站"""
    choice = input("是否发布网站 (执行 'hugo')? (Y/N): ").upper()
    if choice == 'Y':
        print("正在发布网站...")
        publish_process = subprocess.Popen(["hugo"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = publish_process.communicate()
        print("发布输出:", stdout.decode())
        if stderr:
            print("错误信息:", stderr.decode())
        print("网站发布完成。")
    elif choice == 'N':
        print("程序已终止。")
    else:
        print("无效的输入，重新选择。")
        ask_to_publish_site()

def main():
    chosen_dir = choose_directory()
    print(f"选择的目录是: {chosen_dir}")
    os.chdir(chosen_dir)
    run_hugo_server()
    ask_to_publish_site()

if __name__ == "__main__":
    main()
