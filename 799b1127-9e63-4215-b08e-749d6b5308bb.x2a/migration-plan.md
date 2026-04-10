# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three primary Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the interdependencies between services and the need to maintain security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate management, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external cookbook dependencies
- `Policyfile.rb`: Chef policy file defining the run list and cookbook dependencies
- `solo.json`: Configuration data for Chef solo, contains site configurations and security settings
- `solo.rb`: Chef solo configuration file defining paths and log settings
- `Vagrantfile`: Defines the development VM using Fedora 42, with port forwarding and network configuration
- `vagrant-provision.sh`: Bash script to provision the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with development environment using Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or create a custom role
- **ssl_certificate (~> 2.1)**: Use Ansible's built-in OpenSSL modules for certificate management
- **memcached (~> 6.0)**: Use Ansible Galaxy memcached role or create custom role
- **redisio (~> 7.2.4)**: Use Ansible Galaxy redis role or create custom role
- **PostgreSQL**: Use Ansible Galaxy postgresql role or built-in PostgreSQL modules

### Security Considerations

- **SSL Certificate Management**: Migrate certificate generation and installation logic, ensuring private keys remain secure
- **Redis Authentication**: Ensure Redis password is stored securely using Ansible Vault
- **PostgreSQL Credentials**: Store database credentials in Ansible Vault
- **Security Hardening**: Maintain fail2ban, ufw, and SSH hardening configurations
- **FastAPI Environment Variables**: Store sensitive environment variables using Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts with SSL will require careful templating in Ansible
- **Redis Configuration Customization**: The current implementation includes a Ruby block to modify Redis configuration which will need a different approach in Ansible
- **Service Orchestration**: Ensuring proper service restart ordering and notification between dependent services
- **Idempotent Database Setup**: Ensuring PostgreSQL user and database creation is idempotent

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create base Nginx role
   - Implement SSL certificate management
   - Configure virtual hosts
   - Implement security hardening

2. **cache** (moderate complexity)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (high complexity)
   - Implement PostgreSQL database setup
   - Configure Python environment and application deployment
   - Set up systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based systems
2. The self-signed SSL certificates approach will be maintained rather than switching to Let's Encrypt
3. The current security hardening approach (fail2ban, ufw, SSH settings) is sufficient
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis password and PostgreSQL credentials will be migrated as-is initially
6. The Vagrant development environment will be maintained but converted to use Ansible provisioner
7. No additional monitoring or logging solutions need to be implemented beyond what's in the current Chef setup