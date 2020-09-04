# SSH & SCP Client

Python script to automate tasks on a remote machine through SSH/SCP.

## Installation

Clone this repository using ```git clone https://github.com/jaza-k/sshclient.git```
Create a virtual environment with ```python3 -m venv myenv```
Run ```pip3 install -r requirements.txt``` to install the required dependencies

## Usage

Modify the environment variables in the **.env.example** file and rename it to **.env**

`REMOTE_HOST`: IP address or URL of remote host
`REMOTE_USERNAME`: Username for remote host
`SSH_KEY`: /path/to/remote/host/sshkey
`REMOTE_PATH`: Remote directory to serve as destination for file uploads