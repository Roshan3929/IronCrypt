# Use Ubuntu 20.04 as the base image
FROM ubuntu:20.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages: SSH server, Python3 (for Ansible), and sudo
RUN apt-get update && apt-get install -y openssh-server python3 sudo

# Create a non-root user for Ansible to connect as
RUN useradd -m -s /bin/bash ansible
# Set a password for the user (can be useful for debugging)
RUN echo "ansible:ansible" | chpasswd
# Add the user to the sudo group to allow privileged operations
RUN adduser ansible sudo

# Create the .ssh directory for the ansible user
RUN mkdir -p /home/ansible/.ssh
RUN chown ansible:ansible /home/ansible/.ssh

# Create an empty authorized_keys file and set correct permissions
# The public key will be copied into this file.
RUN touch /home/ansible/.ssh/authorized_keys
RUN chmod 700 /home/ansible/.ssh
RUN chmod 600 /home/ansible/.ssh/authorized_keys
RUN chown ansible:ansible /home/ansible/.ssh/authorized_keys

# Copy the public SSH key into the container to authorize connections.
# This key will be generated locally in the next steps.
COPY docker_ssh/id_rsa.pub /home/ansible/.ssh/authorized_keys

# Allow passwordless sudo for the ansible user
RUN echo "ansible ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Create the directory for the SSH service to run
RUN mkdir /var/run/sshd

# Expose the SSH port
EXPOSE 22

# Start the SSH server when the container launches
CMD ["/usr/sbin/sshd", "-D"] 