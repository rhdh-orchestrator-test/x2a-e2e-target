# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, involving three primary cookbooks with external dependencies. Based on the complexity and number of components, we estimate a 2-3 week timeline for complete migration, with an additional week for testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database provisioning, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (both local and external from Chef Supermarket). Migration will require mapping these dependencies to Ansible Galaxy roles or collections.
- `solo.json`: Contains the Chef run list and node attributes. Will need to be converted to Ansible inventory variables.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM using Fedora 42. Can be adapted for Ansible testing with minimal changes.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef. Will need to be replaced with Ansible provisioning.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) based on cookbook metadata, with Fedora 42 used in the Vagrant development environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider based on the Vagrantfile configuration.
- **Cloud Platform**: No specific cloud platform dependencies identified. The configuration appears to be designed for on-premises or generic VM deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or the `ansible.posix.nginx` collection
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role
- **PostgreSQL**: Replace with Ansible's `geerlingguy.postgresql` role or the `community.postgresql` collection

### Security Considerations

- **SSL Certificate Management**: 
  - The current implementation generates self-signed certificates
  - Migration approach: Use Ansible's `community.crypto` collection for certificate generation
  - Consider integrating with Let's Encrypt for production environments

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's `ansible.posix.firewalld` or `community.general.ufw` modules

- **Fail2ban Configuration**:
  - Migration approach: Use Ansible's `community.general.fail2ban` module

- **SSH Hardening**:
  - Migration approach: Use Ansible's `ansible.posix.sshd` module or `dev-sec.ssh-hardening` role

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the FastAPI recipe (`fastapi:fastapi_password`)
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation uses Chef templates to generate site configurations dynamically
  - Mitigation: Use Ansible templates with similar logic, leveraging host_vars or group_vars for site-specific configuration

- **Redis Configuration Hack**: 
  - Description: The cache cookbook includes a Ruby block to modify Redis configuration files after they're created
  - Mitigation: Use Ansible templates with proper configuration options or lineinfile module to ensure correct configuration

- **Service Orchestration**: 
  - Description: The current implementation manages service dependencies and notifications
  - Mitigation: Use Ansible handlers and proper task ordering to ensure services are restarted when configurations change

- **PostgreSQL User and Database Creation**:
  - Description: The current implementation uses shell commands to create database users and permissions
  - Mitigation: Use Ansible's PostgreSQL modules for idempotent database management

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Begin with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement security hardening (fail2ban, firewall)
   - Configure virtual hosts

2. **cache** (moderate complexity)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database and user
   - Deploy application code from Git
   - Configure Python environment and dependencies
   - Set up systemd service

### Assumptions

1. **Environment Configuration**: The current setup assumes development/testing environment (self-signed certificates, Vagrant VM). Production deployment may require additional security considerations.

2. **Network Configuration**: The configuration assumes specific network settings (192.168.121.10 IP address, port forwarding) that may need adjustment in the target environment.

3. **User Management**: The current configuration doesn't explicitly manage system users beyond service accounts. Additional user management may be required.

4. **Backup and Recovery**: No backup mechanisms are defined in the current configuration. This should be addressed in the Ansible implementation.

5. **Monitoring**: No monitoring solutions are configured. Consider adding monitoring as part of the Ansible implementation.

6. **SSL Certificate Authority**: Self-signed certificates are used for development. Production environments should use proper CA-signed certificates.

7. **Database Initialization**: The FastAPI application may require database schema initialization not covered in the current configuration.