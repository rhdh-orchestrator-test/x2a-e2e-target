# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations need careful migration
- Secrets management needs to be implemented with Ansible Vault

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, including security hardening
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4). These will need to be replaced with Ansible Galaxy roles.
- `solo.json`: Contains the run list and configuration data for the Chef run, including Nginx site configurations and security settings.
- `solo.rb`: Chef Solo configuration file that defines paths and log settings.
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding for testing. This can be adapted for Ansible testing.
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks. Will need to be replaced with Ansible provisioning.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ mentioned in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with `ansible.posix.nginx` role or `geerlingguy.nginx` from Ansible Galaxy
- **memcached (~> 6.0)**: Replace with `geerlingguy.memcached` from Ansible Galaxy
- **redisio (~> 7.2.4)**: Replace with `geerlingguy.redis` or `DavidWittman.redis` from Ansible Galaxy

### Security Considerations

- **SSL Certificate Management**: 
  - The current implementation generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation or integrate with Let's Encrypt using `geerlingguy.certbot`

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migration approach: Use Ansible's `ansible.posix.firewalld` or `community.general.ufw` modules

- **Fail2ban Configuration**: 
  - Current implementation installs and configures fail2ban
  - Migration approach: Use `geerlingguy.security` role or create a dedicated fail2ban role

- **SSH Hardening**: 
  - Current implementation disables root login and password authentication
  - Migration approach: Use `dev-sec.ssh-hardening` role or Ansible's `ansible.posix.sshd` module

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe
  - PostgreSQL credentials are hardcoded in the recipe
  - Migration approach: Move all credentials to Ansible Vault and use `ansible.builtin.include_vars` to load them

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: The current implementation dynamically creates virtual hosts based on a data structure
  - Mitigation: Use Ansible templates with loops to generate the same configuration structure

- **Redis Configuration Customization**: 
  - Challenge: The current implementation includes a Ruby block to modify Redis configuration
  - Mitigation: Use Ansible templates with proper variable substitution or use `ansible.builtin.lineinfile` module

- **FastAPI Application Deployment**: 
  - Challenge: The current implementation clones a Git repository and sets up a Python environment
  - Mitigation: Use Ansible's `ansible.builtin.git` module and create a role for Python application deployment

### Migration Order

1. **nginx-multisite** (Priority 1)
   - This is the foundation for the web infrastructure
   - Create base Nginx role with SSL support
   - Add multi-site configuration capability
   - Implement security hardening

2. **cache** (Priority 2)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper integration with Nginx

3. **fastapi-tutorial** (Priority 3)
   - Set up PostgreSQL database
   - Deploy Python application
   - Configure systemd service
   - Integrate with Nginx and caching services

### Assumptions

1. The target environment will continue to be Fedora 42 or similar Linux distributions.
2. Self-signed certificates are acceptable for development, but production may require proper certificates.
3. The same security measures (fail2ban, UFW, SSH hardening) will be maintained.
4. The FastAPI application repository will remain available at the specified URL.
5. The current Redis and PostgreSQL passwords are development credentials and will be replaced in production.
6. The Vagrant setup is primarily for development and testing, not production deployment.
7. No custom Chef resources are being used that would require special handling in Ansible.