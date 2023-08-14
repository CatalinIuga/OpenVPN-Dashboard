
import os
import re
import subprocess

transfer_speeds = {}


def get_clients():
    global transfer_speeds
    command = "cat /etc/openvpn/easy-rsa/pki/index.txt | grep ^V | awk -F \"/\" '{print $2}' | sed 's/CN=//'"
    certificates = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    names = certificates.stdout.read().decode('utf-8').split('\n')[:-1]

    client_list = [
        {
            "name": name,
            "connected": False,
            "real_ip": None,
            "bytes_recv": 0,
            "bytes_sent": 0,
            "connected_since": None,
            "virtual_ip": None,
            "last_ref": None
        }
        for name in names if 'server' not in name
    ]

    process = subprocess.Popen(["timeout", "0.1s", "tail", "-f", "/var/log/openvpn/status.log"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stderr_output = process.stderr.read().decode('utf-8')
    if stderr_output != '':
        print(stderr_output)
        exit(0)
    else:
        stdout_output = process.stdout.read().decode('utf-8')

    client_info_pattern = r'([a-zA-Z0-9_]*),([0-9.:]*),([0-9]*),([0-9]*),([0-9 -:]*)$'
    client_info_matches = re.findall(
        client_info_pattern, stdout_output, re.MULTILINE)

    for match in client_info_matches:
        common_name, real_address, bytes_received, bytes_sent, connected_since = match
        for client in client_list:
            if client["name"] == common_name:
                client["connected"] = True
                client["real_ip"] = real_address
                client["bytes_recv"] = int(bytes_received) / 1000
                client["bytes_sent"] = int(bytes_sent) / 1000
                client["connected_since"] = connected_since

    routing_info_pattern = r'([0-9.:]*),([a-zA-Z0-9_]*),([0-9.:]*),([0-9 -:]*)$'
    routing_info_matches = re.findall(
        routing_info_pattern, stdout_output, re.MULTILINE)

    for match in routing_info_matches:
        virtual_address, common_name, real_address, last_ref = match
        for client in client_list:
            if client["name"] == common_name:
                client["virtual_ip"] = virtual_address
                client["last_ref"] = last_ref

    return client_list


def get_config(name):
    if name == None:
        return None

    for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|', ' ', "."]:
        name = name.replace(char, '')

    print(name)
    username = os.getlogin()
    path = "/home/" + username + "/" + name + ".ovpn"

    if os.path.isfile(path):
        return path
    else:
        return None


def revoke_client(name):
    cmd = 'tail -n +2 /etc/openvpn/easy-rsa/pki/index.txt | grep "^V" | cut -d \'=\' -f 2'
    process = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    clients = process.stdout.read().decode('utf-8').split('\n')[:-1]

    if name not in clients:
        return None

    else:
        index = clients.index(name) + 1

    username = os.getlogin()
    cmd = "/home/" + username + "/openvpn-install.sh"
    process = subprocess.Popen(
        cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = process.communicate(
        input=b"2\n" + str(index).encode('utf-8') + b"\n")[0].decode('utf-8')
    if "Revocation was successful" in result:
        return True
    return False


def create_client(name):
    command = "cat /etc/openvpn/easy-rsa/pki/index.txt | grep ^V | awk -F \"/\" '{print $2}' | sed 's/CN=//'"
    certificates = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    names = certificates.stdout.read().decode('utf-8').split('\n')[:-1]
    if name in names:
        return None

    username = os.getlogin()

    cmd = "/home/" + username + "/openvpn-install.sh"
    process = subprocess.Popen(
        cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    result = process.communicate(
        input=b"1\n" + name.encode('utf-8') + b"\n1\n")[0].decode('utf-8')

    if "Download the .ovpn" in result:
        return True
    return False
