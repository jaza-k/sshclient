"""Client to handle connections and actions executed against a remote host."""

from .log import logger
from os import system
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.auth_handler import AuthenticationException, SSHException
from scp import SCPClient, SCPException

class RemoteClient:
    """Client to interact w/ a remote host via SSH & SCP."""

    def __init__(self, host, user, ssh_key_filepath, remote_path):
        self.host = host
        self.user = user
        self.ssh_key_filepath = ssh_key_filepath
        self.remote_path = remote_path
        self.client = None # serves as the connection objection, None until explicitly connected to remote host
        self.conn = None
        self.scp = None
        self._upload_ssh_key() # run function whenever client is instantiated

    @logger.catch
    def _get_ssh_key(self):
        """Fetch locally stored SSH key."""

        try:
            self.ssh_key = RSAKey.from_private_key_file(self.ssh_key_filepath)
            logger.info('Found SSH key at self {self.ssh_key_filepath}')
        except SSHException as error:
            logger.error(error)
        return self.ssh_key

    @logger.catch
    def _upload_ssh_key(self):
        """Check for local SSH keys to pass to remote host."""

        try:
            system('ssh-copy-id -i {self.ssh_key_filepath}.pub {self.user}@{self.host}>/dev/null 2>&1') # pass bash command that uploads SSH key to remote machine
            logger.info('{self.ssh_key_filepath} uploaded to {self.host}')
        except FileNotFoundError as error:
            logger.error(error)

    @logger.catch
    def _connect(self):
        """Open connection to remote host."""

        if self.conn is None:
            try:
                self.client = SSHClient() # create an object representing SSH client
                self.client.load_system_host_keys() # instruct client to look for known hosts
                self.client.set_missing_host_key_policy(AutoAddPolicy()) # auto add a missing key locally
                self.client.connect(self.host, username=self.user, port=3056, key_filename=self.ssh_key_filepath, look_for_keys=True, timeout=5000)
                self.scp = SCPClient(self.client.get_transport())
            except AuthenticationException as error:
                logger.error('Authentication failed: did you remember to create an SSH key? {error}')
                raise error
        return self.client

    def disconnect(self):
        """Close SSH & SCP connection."""

        if self.client:
            self.client.close()
        if self.scp:
            self.scp.close()

    @logger.catch
    def bulk_upload(self, files):
        """Upload multiple files to a remote directory."""

        self.conn = self._connect()
        uploads = [self._upload_single_file(file) for file in files]
        logger.info('Uploaded {len(uploads)} files to {self.remote_path} on {self.host}')

    def _upload_single_file(self, file):
        """Upload a single file to a remote directory."""
        upload = None
        try:
            self.scp.put(file, recursive=True, remote_path=self.remote_path)
            upload = file
        except SCPException as error:
            logger.error(error)
            raise error
        finally:
            logger.info('Uploaded {file} to {self.remote_path}')
            return upload

    def download_file(self, file):
        """Download file from remote host."""
        
        self.conn = self.connect()
        self.scp.get(file)

    @logger.catch
    def execute_commands(self, commands):
        """Execute multiple commands on remote host in succession."""

        self.conn = self._connect()
        for cmd in commands:
            stdin, stdout, stderr = self.client.exec_command(cmd)
            stdout.channel.recv_exit_status()
            response = stdout.readlines()
            for line in response:
                logger.info('INPUT: {cmd} | OUTPUT: {line}')