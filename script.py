import subprocess

process = subprocess.Popen(["timeout", "0.1s", "sudo", "tail", "-f", "/var/log/openvpn/status.log"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(process.stdout.read().decode('utf-8'))

clients = subprocess.Popen(["sudo", "cat", "/etc/openvpn/ipp.txt"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(clients.stdout.read().decode('utf-8'))

script = subprocess.Popen(["sudo", "openvpn-install.sh"],
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(script.communicate(input=b'4\n')[0].decode('utf-8'))
