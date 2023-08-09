import os
import subprocess

if os.getuid() != 0:
    print("Please run as SUDO!")
    exit(1)

connected = subprocess.Popen(["timeout", "0.1s", "tail", "-f", "/var/log/openvpn/status.log"],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if connected.stderr.read().decode('utf-8') != '':
    print(connected.stderr.read().decode('utf-8'))
else:
    print(connected.stdout.read().decode('utf-8'))

clients = subprocess.Popen(["cat", "/etc/openvpn/ipp.txt"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(clients.stdout.read().decode('utf-8'))

script = subprocess.Popen(["sudo", "openvpn-install.sh"],
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(script.communicate(input=b'4\n')[0].decode('utf-8'))