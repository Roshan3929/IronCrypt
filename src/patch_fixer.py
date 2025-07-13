import paramiko

def execute_patch(ip: str, username: str, private_key_path: str, patch_command: str):
    """
    Executes a patch command on a remote host via SSH using key-based authentication.
    """
    try:
        # Load the private key for authentication
        key = paramiko.RSAKey.from_private_key_file(private_key_path)
        
        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the remote host
        ssh.connect(hostname=ip, username=username, pkey=key)

        # Execute the command
        stdin, stdout, stderr = ssh.exec_command(patch_command)
        out = stdout.read().decode()
        err = stderr.read().decode()
        exit_status = stdout.channel.recv_exit_status()

        # Close the connection
        ssh.close()

        return {
            "success": exit_status == 0,
            "stdout": out,
            "stderr": err,
            "exit_code": exit_status
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        } 