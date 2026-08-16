# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No complex custom resources or libraries
- Standard infrastructure components (Nginx, FastAPI, Redis, Memcached)
- Security configurations that need careful migration

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
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef Solo configuration - not needed in Ansible
- `Vagrantfile`: Defines the development VM - can be adapted for Ansible provisioning
- `vagrant-provision.sh`: Provisions the VM with Chef - will be replaced with Ansible provisioning

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation and configuration
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should:
  - Maintain the same certificate generation approach
  - Consider adding Let's Encrypt integration as an improvement
  - Ensure proper permissions on private keys

- **Firewall Configuration**: The current implementation uses UFW:
  - Migrate to appropriate firewall module (firewalld for Fedora/RHEL, ufw for Ubuntu)
  - Maintain the same port allowances (SSH, HTTP, HTTPS)

- **SSH Hardening**: Maintain the same security settings:
  - Disable root login
  - Disable password authentication

- **Fail2ban Configuration**: Migrate the fail2ban configuration to Ansible

- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: User "fastapi" with password "fastapi_password"
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: The current implementation uses a template to generate site configurations. Ansible will need to:
  - Maintain the same template-based approach
  - Ensure proper SSL configuration for each site

- **Service Dependencies**: The FastAPI application depends on PostgreSQL. Ansible will need to:
  - Ensure proper ordering of tasks
  - Use handlers for service restarts
  - Consider using wait_for to ensure services are ready

- **Custom Security Configurations**: The current implementation includes custom sysctl settings and security configurations. Ansible will need to:
  - Maintain the same security settings
  - Use appropriate Ansible modules for sysctl configuration

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component
   - Other components depend on it
   - Start with basic Nginx installation and configuration
   - Add SSL and security features
   - Finally, add multi-site configuration

2. **cache** (Priority 2)
   - Independent service
   - Relatively simple configuration
   - Depends on external roles (memcached, redis)

3. **fastapi-tutorial** (Priority 3)
   - Application deployment
   - Depends on PostgreSQL
   - More complex with Python environment setup and application deployment

### Assumptions

1. The target environment will continue to be Fedora 42 or similar Linux distributions.
2. Self-signed certificates are acceptable for the migrated solution (not production-ready).
3. The same security hardening measures should be maintained in the Ansible solution.
4. The directory structure for web content (/var/www/[site]) should be preserved.
5. The PostgreSQL database configuration for FastAPI should remain the same.
6. Redis and Memcached configurations should maintain the same settings.
7. The Vagrant development environment should be preserved but updated to use Ansible.