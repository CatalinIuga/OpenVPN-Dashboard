# OpenVPN Admin Dashboard

## Description

This is a simple dashboard for managing OpenVPN users. It is written in Python using the Flask framework and TailwindCSS for the frontend.

```bash
flask --app app run --debug
```

## Features

- Create and delete clients
- Download user configuration files
- View conected clients

## TODO

- add .env file and use to store the secret key and the passwordhash
- endpoints
  - /api/clients -> get all clients
  - /api/clients/status -> get connected clients and their status
  - /api/clients/<client_name> -> GET/POST/DELETE client
  

<!--
# IPV6? am uitat de el oopsie!

# sudo cat /etc/openvpn/ipp.txt

# sudo tail /var/log/openvpn/status.log

# - need to find conf files for each user

# - figure out input sequence for each user for revoking/creating script -->
