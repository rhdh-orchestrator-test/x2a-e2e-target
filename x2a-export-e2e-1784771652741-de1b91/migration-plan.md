# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations need careful migration to maintain hardening standards

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom Nginx configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, service management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file listing both local and external cookbooks. Contains references to nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4) cookbooks from the Chef Supermarket.
- `solo.json`: Configuration data for Chef Solo with run list and node attributes. Contains site configurations, SSL paths, and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding for development and testing.
- `vagrant-provision.sh`: Bash script to install Chef and run the cookbooks in the Vagrant environment.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible Galaxy `geerlingguy.memcached` role or direct package management
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy `geerlingguy.redis` role or custom Redis configuration tasks

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW. Migration should use Ansible's `ufw` module or `firewalld` module depending on target OS.
- **Fail2ban Setup**: Current Chef cookbook configures fail2ban with custom jail settings. Use Ansible to manage fail2ban configuration.
- **SSH Hardening**: The cookbook disables root login and password authentication. Ensure these security measures are maintained in Ansible.
- **SSL Certificate Management**: Self-signed certificates are generated for each site. Consider using Ansible's `openssl_*` modules or integrating with Let's Encrypt via `geerlingguy.certbot`.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - No external vault integration is currently used

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically creates site configurations based on node attributes. Ansible templates will need to replicate this functionality.
- **SSL Certificate Generation**: Self-signed certificates are generated for each site. Ansible will need to handle certificate creation and management.
- **Service Orchestration**: The current setup manages multiple interdependent services (Nginx, PostgreSQL, Redis, Memcached, FastAPI application). Ansible will need to maintain proper ordering and notifications.
- **Python Application Deployment**: The FastAPI application deployment includes git clone, venv setup, and systemd service configuration. This workflow needs to be preserved in Ansible.

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
   - Create base Nginx role with templates
   - Add SSL certificate management
   - Implement security hardening (fail2ban, ufw)
   - Configure virtual hosts

2. **cache** (Priority 2): Supporting services with moderate complexity
   - Implement Memcached configuration
   - Set up Redis with authentication
   - Configure service management

3. **fastapi-tutorial** (Priority 3): Application deployment with database dependencies
   - Set up PostgreSQL database
   - Implement Python application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora/RHEL-based systems, though the cookbooks support Ubuntu as well.
2. Self-signed certificates are acceptable for the migrated solution, though integration with Let's Encrypt could be considered.
3. The Vagrant development environment will be maintained, but converted to use Ansible provisioner instead of Chef.
4. The current security hardening approach (fail2ban, ufw, SSH hardening) is appropriate and should be maintained.
5. The FastAPI application source will continue to be available at the specified Git repository.
6. Redis and PostgreSQL passwords in the current implementation are for development only and will be replaced with more secure credential management in production.
7. The current directory structure with separate roles for each component will be maintained in the Ansible repository.