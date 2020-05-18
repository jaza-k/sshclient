import sys
from loguru import logger
from os import system
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.auth_handler import AuthenticationException, SSHException
from scp import SCPClient, SCPException

logger.add(sys.stderr, format="{time} {level} {message}", filter="client", level="INFO")
logger.add('logs/log_{time:YYYY-MM-DD}.log', format="{time} {level} {message}", filter="client", level="ERROR")

class RemoteClient:
    """Client to interact w/ a remote host wia SSH & SCP."""

    def __init__(self, host, user, ssh_key_filepath, remote_path):
        self.host = host
        self.user = user
        self.ssh_key_filepath = ssh_key_filepath
        self.remote_path = remote_path
        self.client = None # serves as the connection objection, None until explicitly connected to remote host
        self.scp = None
        self.__upload_ssh_key() # run function whenever client is instantiated

    def __get_ssh_key(self):
        """Fetch locally stored SSH key."""

        try:
            self.ssh_key = RSAKey.from_private_key_file(self.ssh_key_filepath)
            logger.info('Found SSH key at self {self.ssh_key_filepath}')
        except SSHException as error:
            logger.error(error)
        return self.ssh_key

    def __upload_ssh_key(self):
        try:
            system('ssh-copy-id -i {self.ssh_key_filepath} {self.user}@{self.host}>/dev/null 2>&1')
            system('ssh-copy-id -i {self.ssh_key_filepath}.pub {self.user}@{self.host}>/dev/null 2>&1')
            logger.info('{self.ssh_key_filepath} uploaded to {self.host}')
        except FileNotFound as error:
            logger.error(error)

    def __connect(self):
        """Open connection to remote host."""

        try:
            self.client = SSH.client() # create an object representing SSH client
            self.client.load_system_host_keys() # instruct client to look for known hosts
            self.client.set_missing_host_key_policy(AutoAddPolicy()) # auto add a missing key locally
            self.client.connect(self.host, username=self.user, key_filename=self.ssh_key_filepath, look_for_keys=True, timeout=5000)
            self.scp = SCPClient(self.client.get_transport())
        except AuthenticationException as error:
            logger.info('Authentication failed: did you remember to create an SSH key?')
            logger.error(error)
            raise error
        finally:
            return self.client

    def disconnect(self):
        """Close SSH connection."""

        self.client.close()
        self.scp.close()
    
    def execute_commands(self, commands):
        """Execute multiple commands in succession."""

        if self.client is None:
            self.client = self.__connect()
        for cmd in commands:
            stdin, stdout, stderr = self.client.exec_command(cmd)
            stdout.channel.recv_exit_status()
            response = stdout.readLines()
            for line in response:
                logger.info('INPUT: {cmd} | OUTPUT: {line}')

