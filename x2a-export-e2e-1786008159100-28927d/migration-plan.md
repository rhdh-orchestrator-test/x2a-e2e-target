# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server setup with caching services (Redis and Memcached) and a FastAPI application. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and resources to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No custom Chef resources except for a simple lineinfile resource
- Standard web server, caching, and application deployment patterns
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom site templates

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
- `solo.rb`: Chef configuration file - will be replaced by Ansible configuration
- `Vagrantfile`: Defines the development VM - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisions the VM with Chef - will be replaced with Ansible provisioning

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability while allowing for future integration with Let's Encrypt.
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation

- **Firewall Configuration (UFW)**: The current implementation configures UFW with specific rules.
  - Migration approach: Use Ansible's `ufw` module to configure firewall rules

- **Fail2Ban Configuration**: The current implementation installs and configures fail2ban.
  - Migration approach: Use Ansible's `template` module to configure fail2ban with the same settings

- **SSH Hardening**: The current implementation disables root login and password authentication.
  - Migration approach: Use Ansible's `lineinfile` module or the `ansible.posix.sshd` module to configure SSH

- **Vault/secrets management**:
  - Redis password in cache cookbook: Replace with Ansible Vault
  - PostgreSQL credentials in fastapi-tutorial cookbook: Replace with Ansible Vault
  - Count: 2 credentials detected (Redis password, PostgreSQL user/password)

### Technical Challenges

- **Custom Resource Migration**: The `lineinfile` custom resource needs to be replaced with Ansible's native `lineinfile` module.
  - Mitigation: Ansible's built-in module provides similar functionality, making this a straightforward migration.

- **Template Conversion**: Chef ERB templates need to be converted to Jinja2 for Ansible.
  - Mitigation: Create a template conversion guide for the team to ensure consistent translation of template syntax.

- **Attribute to Variable Mapping**: Chef node attributes need to be mapped to Ansible variables.
  - Mitigation: Create a mapping document that shows the relationship between Chef attributes and Ansible variables.

- **Service Management**: The FastAPI application uses systemd service management that needs to be recreated in Ansible.
  - Mitigation: Use Ansible's `systemd` module to manage the service with the same configuration.

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Supporting service with external dependencies (memcached, redis)
   - Moderate complexity with authentication configuration

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on the infrastructure being in place
   - Involves database setup, application code deployment, and service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. Self-signed certificates are acceptable for the migrated solution (not production-ready).
3. The same directory structure for web content will be maintained.
4. The FastAPI application source will continue to be available at the specified Git repository.
5. The Vagrant development environment will be maintained for testing.
6. No additional features beyond what's in the current Chef implementation are required.
7. The security configurations (fail2ban, ufw, SSH hardening) are still relevant and required.
8. Redis and Memcached versions compatible with the application will be available in the target environment.