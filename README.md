# BACnet improvements

## Introduction

This repository contains a set of scripts for exploiting certain system vulnerabilities, performing health checks, and handling setup/reset processes. Additionally, it includes a Chaos Monkey script for resilience testing and instructions for setting up a VPN. The key scripts included are:

- `exploit1.py`
- `exploit2.py`
- `exploit3.py`
- `health.sh`
- `reset.sh`
- `setup.sh`
- `chaosmonkey.sh`

**Note**: Use these scripts responsibly and only in authorized environments.

## Table of Contents

- [Introduction](#introduction)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Exploits](#exploits)
  - [Health Check](#health-check)
  - [Setup and Reset](#setup-and-reset)
  - [Chaos Monkey](#chaos-monkey)
  - [VPN Setup](#vpn-setup)
- [Contributing](#contributing)
- [License](#license)

## System Requirements

- Ubuntu 22.04 VM (For VPN testing, it is recommended to start another Ubuntu VM)
- Bridged network adapter (NAT also works but is less convenient for using VPN)

## Installation

Follow these steps to install the application:

1. Install Docker by following the instructions at [Docker Installation Guide](https://docs.docker.com/engine/install/ubuntu/).
2. Install WireGuard tools:

    ```bash
    sudo apt install wireguard-tools
    ```

3. Place the provided zip file on the Ubuntu machine.
4. Run the following command to reset the environment (for safety):

    ```bash
    sudo ./<project-folder>/reset.sh
    ```

5. To start everything, run:

    ```bash
    sudo ./<project-folder>/setup.sh
    ```

6. To keep the environment running, you can optionally run:

    ```bash
    sudo ./<project-folder>/health.sh
    ```

    (This is not necessary for the application to function.)

7. Access the web portal at:

    ```
    https://<ip address>:5000
    ```

## Usage

### Logging into the Web Server

1. Enter the username and password (for Admin account use `admin:admin`, for User account use `user:user`).
2. Execute the following command to find the secret key for MFA:

    ```bash
    docker exec -it mysql mysql -u beheer -p xxx -e 'select * from db.users'
    ```

3. Find the `secret_key` for the user from the output.
4. Enter the MFA secret key into a Google Authenticator application (mobile app or browser extension).
5. Use the generated code as the MFA code to log in.

### Exploits

The exploit scripts are designed to target specific vulnerabilities. Each script might have different requirements and functionalities.

#### `exploit1.py`

```bash
python3 exploit1.py
```

#### `exploit2.py`

```bash
python3 exploit2.py
```

#### `exploit3.py`

```bash
python3 exploit3.py
```

### Health Check

The `health.sh` script checks the health status of the system. To run it, execute:

```bash
./health.sh
```

### Setup and Reset

#### Setup

The `setup.sh` script prepares the environment. Run it using:

```bash
./setup.sh
```

#### Reset

The `reset.sh` script resets the environment to its initial state. Execute it with:

```bash
./reset.sh
```

### Chaos Monkey

The `chaosmonkey.sh` script simulates random failures in the system to test its resilience. To use it, run:

```bash
./chaosmonkey.sh
```

### VPN Setup

Follow these steps to set up the VPN:

1. Install the second Ubuntu VM (preferably in bridged mode).
2. Install WireGuard tools:

    ```bash
    sudo apt install wireguard-tools
    ```

3. Copy the `wg0.conf` file from `<project-folder>/vpn/remote/` to the remote host's `/etc/wireguard` directory.
4. Edit the `wg0.conf` file to update the `endpoint` field to the IP of the machine where the application is running.
5. Start the VPN by running:

    ```bash
    sudo wg-quick up wg0
    ```

## Contributing

Contributions are welcome! Please fork this repository and submit pull requests with any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
her specific details relevant to your project. If there are any additional instructions or prerequisites for the scripts, make sure to include those as well.
