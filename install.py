import sys
import paramiko
import subprocess

# Получение загрузки сервера 
def get_load(ip, key):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Подключаемся к {ip}")
    ssh.connect(ip, username="root", key_filename=key)
    stdin, stdout, stderr = ssh.exec_command("uptime")
    output = stdout.read().decode()
    ssh.close()
    print(f"Результат: {output.strip()}")
    load_avg = float(output.strip().split("load average:")[1].split(",")[0])
    return load_avg

# Запуск Ansible
def run_ansible(target_ip, second_ip):
    print(f"Устанавливаем PostgreSQL на {target_ip}")
    env = {"TARGET_IP": target_ip, "SECOND_IP": second_ip}
    result = subprocess.run([
        "ansible-playbook", "-i", f"{target_ip},", "ansible/playbook.yml",
        "--private-key=config/id_ed25519", "-u", "root"
    ], env={**env, **dict(**env)})
    if result.returncode == 0:
        print("Установка завершена!")
    else:
        print("Ошибка при установке.")

def main():
    if len(sys.argv) != 2:
        print("Использование: python3 install.py ip1,ip2")
        return

    ips = sys.argv[1].split(",")
    ssh_key = "config/id_ed25519"  # путь к приватному ключу

    print("Проверяем нагрузку...")
    load1 = get_load(ips[0], ssh_key)
    load2 = get_load(ips[1], ssh_key)

    if load1 < load2:
        target, second = ips[0], ips[1]
    else:
        target, second = ips[1], ips[0]

    print(f"Выбран сервер: {target}")
    run_ansible(target, second)

if __name__ == "__main__":
    main()

