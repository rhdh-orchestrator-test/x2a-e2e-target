# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations need careful migration
- Hardcoded secrets need to be addressed

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, dependency on community cookbooks

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including community cookbooks (nginx, memcached, redisio)
- `solo.json`: Contains node configuration including run list and attributes for Nginx sites and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding for testing
- `vagrant-provision.sh`: Bash script to install Chef and run the cookbooks in the Vagrant environment

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible Galaxy memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy redis role (e.g., geerlingguy.redis)

### Security Considerations

- **Firewall Configuration**: The current setup uses UFW for firewall management. Ansible has dedicated modules for UFW or firewalld depending on the target OS.
  - Migration approach: Use `ansible.posix.firewalld` for Fedora/CentOS and `community.general.ufw` for Ubuntu
  
- **Fail2ban Configuration**: Current setup includes fail2ban for brute force protection.
  - Migration approach: Use Ansible to deploy fail2ban configuration files and manage the service

- **SSH Hardening**: Current setup disables root login and password authentication.
  - Migration approach: Use `ansible.posix.sshd_config` module to manage SSH configuration

- **SSL Certificate Management**: Self-signed certificates are generated for each virtual host.
  - Migration approach: Use `community.crypto.openssl_*` modules to generate certificates

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - Migration approach: Use Ansible Vault to store sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically creates Nginx virtual hosts based on node attributes.
  - Mitigation: Create Ansible templates that can generate site configurations from variables

- **Service Dependencies**: The FastAPI application depends on PostgreSQL being configured first.
  - Mitigation: Use Ansible handlers and proper task ordering to ensure dependencies are met

- **OS-specific Configurations**: The cookbooks support multiple operating systems.
  - Mitigation: Use Ansible facts to determine the OS and apply appropriate configurations

- **Redis Configuration Hacks**: The cache cookbook includes a Ruby block to modify Redis configuration files.
  - Mitigation: Create proper Redis configuration templates in Ansible

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Relatively self-contained with minimal external dependencies

2. **cache** (Priority 2)
   - Depends on community cookbooks that need to be replaced with Ansible Galaxy roles
   - Contains hardcoded credentials that need to be moved to Ansible Vault

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on the infrastructure being in place
   - Involves database setup, application deployment, and service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or similar Linux distributions.
2. The same network configuration (ports, IP addresses) will be maintained.
3. Self-signed certificates are acceptable for the migrated environment (not production).
4. The FastAPI application source will remain available at the same Git repository.
5. The current security practices (fail2ban, UFW, SSH hardening) should be maintained.
6. The migration will address the hardcoded credentials by moving them to Ansible Vault.
7. The Vagrant development environment will be replaced with an equivalent Ansible-based setup.