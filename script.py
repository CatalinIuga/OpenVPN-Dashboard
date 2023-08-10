
import os
import re
import subprocess


def get_clients():
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
        for name in names
    ]

    # print(client_list)
    process = subprocess.Popen(["timeout", "0.1s", "tail", "-f", "/var/log/openvpn/status.log"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stderr_output = process.stderr.read().decode('utf-8')
    if stderr_output != '':
        print(stderr_output)
        exit(0)
    else:
        stdout_output = process.stdout.read().decode('utf-8')

    # Use the provided regex patterns
    client_info_pattern = r'([a-zA-Z0-9_]*),([0-9.:]*),([0-9]*),([0-9]*),([0-9 -:]*)$'
    routing_info_pattern = r'([0-9.:]*),([a-zA-Z0-9_]*),([0-9.:]*),([0-9 -:]*)$'

    # Find all matches of the patterns in the output
    client_info_matches = re.findall(
        client_info_pattern, stdout_output, re.MULTILINE)
    routing_info_matches = re.findall(
        routing_info_pattern, stdout_output, re.MULTILINE)

    # Process client information matches
    for match in client_info_matches:
        common_name, real_address, bytes_received, bytes_sent, connected_since = match
        for client in client_list:
            if 'server' in client["name"]:
                continue
            if client["name"] == common_name:
                client["connected"] = True
                client["real_ip"] = real_address
                client["bytes_recv"] = bytes_received
                client["bytes_sent"] = bytes_sent
                client["connected_since"] = connected_since

    # Process routing information matches
    for match in routing_info_matches:
        virtual_address, common_name, real_address, last_ref = match
        for client in client_list:
            if client["name"] == common_name:
                client["virtual_ip"] = virtual_address
                client["last_ref"] = last_ref

    # Print the extracted client information
    return client_list

# return the path of the client config file
# the files then gets sent as an attachment to the client


def get_config(name):
    if name == None:
        return None

    # sanitize the name from the client
    for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|', ' ', "."]:
        name = name.replace(char, '')

    print(name)
    username = os.getlogin()
    path = "/home/" + username + "/" + name + ".ovpn"

    # check if the file exists
    if os.path.isfile(path):
        return path
    else:
        return None
    

def revoke_client(name):
    if name == None:
        return None

    # sanitize the name from the client
    for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|', ' ', "."]:
        name = name.replace(char, '')
