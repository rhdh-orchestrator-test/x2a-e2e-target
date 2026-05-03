# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security hardening settings.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has well-structured Chef cookbooks with clear separation of concerns
- Security hardening is implemented throughout the codebase
- Multiple external dependencies need to be replaced with Ansible Galaxy roles or custom implementations

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup with self-signed certificates, fail2ban integration, UFW firewall rules, security headers, rate limiting

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, service management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `Vagrantfile`: Defines development VM using Fedora 42 with libvirt provider, port forwarding, and rsync folder sharing
- `solo.json`: Chef configuration with run list and node attributes for nginx sites and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef and Berkshelf

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.nginx role or create a custom role based on the nginx module
- **memcached (~> 6.0)**: Replace with geerlingguy.memcached Ansible Galaxy role
- **redisio (~> 7.2.4)**: Replace with geerlingguy.redis Ansible Galaxy role
- **fail2ban**: Implement using ansible.posix.fail2ban module or geerlingguy.security role
- **ufw**: Implement using ansible.builtin.ufw module
- **PostgreSQL**: Replace with geerlingguy.postgresql or community.postgresql roles

### Security Considerations

- **SSL/TLS Configuration**: Migrate the self-signed certificate generation logic to Ansible using the community.crypto collection
  - Migration approach: Use community.crypto.openssl_* modules to generate self-signed certificates
  
- **Firewall Rules**: Convert UFW rules to Ansible ufw module
  - Migration approach: Use ansible.builtin.ufw module to configure firewall rules

- **fail2ban Configuration**: Convert fail2ban jail configuration to Ansible
  - Migration approach: Use ansible.posix.fail2ban module or templates to configure fail2ban

- **System Hardening**: Convert sysctl security settings to Ansible
  - Migration approach: Use ansible.posix.sysctl module to configure kernel parameters

- **Vault/secrets management**:
  - Redis password in cache cookbook: Store in Ansible Vault
  - PostgreSQL credentials in fastapi-tutorial cookbook: Store in Ansible Vault
  - Count of credentials detected: 2 (Redis password, PostgreSQL user/password)

### Technical Challenges

- **Custom Resource Conversion**: The `lineinfile` custom resource in nginx-multisite needs to be replaced with Ansible's lineinfile module
  - Mitigation: Map the Chef resource properties to Ansible module parameters

- **Template Conversion**: Multiple ERB templates need to be converted to Jinja2 format
  - Mitigation: Carefully convert ERB syntax (`<%= %>`) to Jinja2 (`{{ }}`) while preserving logic

- **Service Management**: Different service management approaches between Chef and Ansible
  - Mitigation: Use Ansible's service module with appropriate handlers for notifications

- **Configuration File Management**: Chef's approach to file management differs from Ansible
  - Mitigation: Use Ansible's template, copy, and file modules with appropriate state parameters

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first
   - Moderate complexity with multiple templates and security configurations

2. **cache** (Priority 2)
   - Depends on external cookbooks (memcached, redisio)
   - Relatively simple configuration but requires secret management
   - Lower complexity than nginx-multisite

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on properly configured infrastructure
   - Contains database setup and application deployment logic
   - Moderate complexity with multiple components (Python, Git, PostgreSQL)

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions
2. The self-signed certificates approach is acceptable for the migrated solution (not using Let's Encrypt or other CA)
3. The current security hardening measures are appropriate and should be maintained
4. The Vagrant development environment will be maintained but converted to use Ansible provisioner
5. No changes to the application code or database schema are required
6. The current directory structure for web content will be preserved
7. The Redis and PostgreSQL passwords in the code are development credentials and will be replaced with proper secrets management
8. The current nginx rate limiting and security headers configuration is appropriate for the target environment
9. The fastapi-tutorial Git repository URL and branch are still valid and accessible
10. The systemd service configuration for the FastAPI application is appropriate for the target environment