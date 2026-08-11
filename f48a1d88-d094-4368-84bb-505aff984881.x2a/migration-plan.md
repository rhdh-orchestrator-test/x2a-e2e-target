# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies on community cookbooks need to be replaced with Ansible equivalents
- Security configurations need careful migration to maintain hardening standards

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), sysctl security settings

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, depends on community cookbooks

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management, Git repository deployment

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains node configuration including the run list and attribute overrides for Nginx sites and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration (Fedora 42) with port forwarding and networking

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata, but the Vagrantfile uses Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or use the `ansible.builtin.package` module with templates
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` role or use the `ansible.builtin.package` module with templates
- **redisio (~> 7.2.4)**: Replace with Ansible's `redis` role or use the `ansible.builtin.package` module with templates

### Security Considerations

- **SSL Certificate Management**: The Chef cookbook generates self-signed certificates. Migrate to Ansible's `openssl_*` modules or consider integrating with `community.crypto.acme_certificate` for Let's Encrypt
- **Firewall Configuration**: UFW firewall rules need to be migrated to Ansible's `community.general.ufw` module
- **fail2ban**: Configuration needs to be migrated to Ansible tasks using templates
- **SSH Hardening**: SSH configuration hardening (disable root login, password authentication) should be migrated to Ansible's `ansible.posix.sshd_config` module
- **Vault/secrets management**:
  - Redis password in the cache cookbook: `redis_secure_password_123`
  - PostgreSQL database credentials in the fastapi-tutorial cookbook: `fastapi:fastapi_password`
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of Nginx site configurations based on node attributes needs to be replicated using Ansible's templating system
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be migrated to Ansible tasks
- **Service Dependencies**: Ensuring proper service dependencies and restart handlers are maintained in Ansible
- **PostgreSQL Configuration**: Database and user creation needs to be migrated to Ansible's PostgreSQL modules
- **Python Application Deployment**: The FastAPI application deployment process needs to be converted to Ansible tasks

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Add security hardening (fail2ban, UFW)
   - Add multi-site configuration

2. **cache** (Priority 2)
   - Memcached and Redis services
   - Ensure proper security configuration for Redis

3. **fastapi-tutorial** (Priority 3)
   - PostgreSQL database setup
   - Python application deployment
   - Service configuration

### Assumptions

1. The target environment will continue to use the same operating systems (Ubuntu/CentOS/Fedora)
2. Self-signed certificates are acceptable for development, but production may require proper certificates
3. The same security hardening standards need to be maintained
4. The FastAPI application source will remain available at the same Git repository
5. The directory structure for web content and configuration files will remain the same
6. The Vagrant development environment will be maintained, but Chef will be replaced with Ansible