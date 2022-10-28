# Sending DRI packets

This document describes the pi/rock used as a centralised controller between the hardware of the DRI in AS0.

[toc]

## Setup Instructions

1. Clone the firmware.
1. Create .env file.
1. Install the dependencies.
1. Setup to start on reboot

### Clone the firmware

You'll need to setup SSH keys on the Pi in order to clone the firmware onto the pi. You can do this with `ssh-keygen`. Use the following command, use the default path, and don't set a password:

```bash
ssh-keygen -t ed25519
```

You'll then need to copy the public key it produces over to github to add it as an SSH key for your account. E.g. if the default path was used on the pi, you should be able to cat it as follows:

```bash
cat /home/pi/.ssh/id_ed25519.pub
```

Once that's setup on github you should be able to clone the firmware onto the pi:

```bash
git@github.com:aero-tracker/aero-sniff.git
```

The firmware will be at `pi-dri`.

### Create .env file

A number of configuration variables need to be set upon installation using a `.env` file which is loaded into our firmware by `consts.py`. An example is provided in this repository, `.env.example` and `consts.py` contains documentation regarding each variable. You should just need to do:

```bash
cp .env.example .env
nano .env
```

Then the variables you will need to change should be as follows:

| Variable name     | Description                                                  |
| ----------------- | ------------------------------------------------------------ |
| `DRI_SENSOR_ID`       | The ID of the sensor. This should be the sniffers serial number. |
| `ENV`            | The environment to define logging level, either dev or prod. |

### Installing Dependencies

Most of the dependencies of the pi's firmware are captured in the [requirements.txt](./requirements.txt) file:

```bash
pip3 install -r requirements.txt
```

Once you've installed the dependencies, check you can run the firmware by doing:

```bash
python3 main.py
```

As long as there are no import errors, everything is fine.

### Setup to start on reboot

We can use Systemctl to setup our main.py to start on reboot. The first step is to create a service file in /lib/systemd/system.

cd /lib/systemd/system
sudo touch detect-on-boot.service
You can then use nano nano detect-on-boot.service to put the following into the service file:

```bash
[Unit]
Description="This service runs /home/root/aerosentry-one/controller-pi/main.py"

[Service]
User=pi

WorkingDirectory=/home/pi
ExecStart=/usr/bin/python3 /home/rock/pi-dri/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

You can then reload the systemctl daemon - the daemon has to be reloaded to pick up our new detect-on-boot.service file.

```bash
systemctl daemon-reload
```

Start the service and check its status to check it works:

```bash
systemctl start detect-on-boot
systemctl status detect-on-boot
```
