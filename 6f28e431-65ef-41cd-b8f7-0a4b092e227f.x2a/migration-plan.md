# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks, their dependencies, and security configurations to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Multiple interconnected services
- Security configurations that need careful migration
- External dependencies on community cookbooks that need Ansible equivalents

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible Galaxy requirements.yml
- `Policyfile.rb`: Chef policy definition - will be replaced by Ansible playbook structure
- `solo.json`: Chef node configuration - will be migrated to Ansible inventory variables
- `solo.rb`: Chef configuration - will be replaced by Ansible configuration
- `Vagrantfile`: Development environment definition - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible playbook calls

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management tasks or community.crypto collection

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should preserve this functionality while allowing for future integration with Let's Encrypt.
- **Firewall Configuration (ufw)**: Current Chef recipes configure ufw. Ansible should use the `ansible.posix.firewalld` or `community.general.ufw` modules.
- **Fail2ban Configuration**: Current Chef recipes configure fail2ban. Ansible should use dedicated fail2ban tasks or community modules.
- **SSH Hardening**: Current Chef recipes disable root login and password authentication. Ansible should use the `ansible.posix.ssh_config` module.
- **Redis Authentication**: Current Chef recipes set a Redis password. Ansible should maintain this security practice.

### Technical Challenges

- **Multi-site Nginx Configuration**: The current Chef cookbook dynamically generates Nginx site configurations. Ansible templates will need to replicate this functionality.
- **Service Orchestration**: The current Chef setup manages service dependencies. Ansible handlers and meta-dependencies will need to be carefully designed.
- **PostgreSQL User and Database Management**: The current Chef recipe uses shell commands for PostgreSQL configuration. Ansible should use the `community.postgresql` collection for better idempotence.
- **Python Environment Management**: The current Chef recipe creates and manages Python virtual environments. Ansible should use the `ansible.builtin.pip` module with virtualenv support.

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Depends on external cookbooks (memcached, redisio)
   - Moderate complexity with Redis authentication

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on infrastructure being in place
   - Involves database setup, application deployment, and service configuration

### Assumptions

1. The target environment will continue to be Fedora/RHEL-based systems, with potential support for Ubuntu/Debian.
2. Self-signed certificates are acceptable for development; production may require integration with a certificate authority.
3. The security configurations (fail2ban, ufw, SSH hardening) are required in the migrated solution.
4. The FastAPI application source will continue to be pulled from the same Git repository.
5. Redis authentication will continue to use password-based authentication rather than more advanced methods.
6. The current multi-site Nginx configuration pattern should be preserved in the Ansible solution.
7. The PostgreSQL database will be local to the application server; no separate database server is configured.