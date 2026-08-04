# MIGRATION FROM CHEF TO ANSIBLE

This migration plan outlines the process of converting the existing Chef cookbooks to Ansible roles and playbooks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and custom site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Contains node configuration including the run list and attributes for Nginx sites and security settings
- `solo.rb`: Chef Solo configuration file defining cookbook paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding for testing the infrastructure
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks in the Vagrant environment

### Target Details

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role from Galaxy or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package management
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` or DavidWittman.redis role

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW with specific rules for SSH, HTTP, and HTTPS.
- **fail2ban Setup**: The cookbook configures fail2ban for intrusion prevention.
- **SSH Hardening**: The cookbook disables root login and password authentication.
- **SSL Certificate Management**: Self-signed certificates are generated for each virtual host.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi`/`fastapi_password`)
  - No external vault integration is present in the current implementation

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically creates Nginx site configurations based on attributes.
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates for each site.
- **Service Orchestration**: The Chef cookbook manages multiple services (Nginx, Redis, Memcached, PostgreSQL, FastAPI application).
- **Python Application Deployment**: The Chef cookbook clones a Git repository and sets up a Python virtual environment.

### Migration Order

1. **nginx-multisite** (Priority 1)
2. **cache** (Priority 2)
3. **fastapi-tutorial** (Priority 3)

### Assumptions

1. **Environment Variables**: The current implementation uses hardcoded values for credentials.
2. **Testing Environment**: The Vagrantfile suggests that testing is done in a local VM environment.
3. **SSL Certificates**: The current implementation generates self-signed certificates.
4. **Operating System Compatibility**: The cookbooks support Ubuntu 18.04+, CentOS 7+, and the Vagrantfile uses Fedora 42.
5. **Service Dependencies**: The FastAPI application depends on PostgreSQL, and the Nginx configuration depends on the application services.
6. **Idempotence**: The Chef recipes include several idempotence checks (e.g., `not_if` guards).
7. **Custom Configuration**: The nginx-multisite cookbook includes custom configuration templates.