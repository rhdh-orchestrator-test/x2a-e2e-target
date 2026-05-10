# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx server with caching services (Memcached and Redis) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3-4 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7-8 weeks

**Complexity Assessment:** Medium
- Multiple interconnected services
- Security configurations that need careful migration
- External dependencies on community cookbooks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Chef Solo configuration file containing the run list and node attributes.
- `solo.rb`: Chef Solo configuration specifying cookbook paths and log settings.
- `Vagrantfile`: Defines the development VM using Fedora 42, with port forwarding and resource allocation.
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in the Vagrant development environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration).
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW. Migration should use Ansible's `ufw` module or `firewalld` module depending on the target OS.
  - Migration approach: Use Ansible's built-in firewall modules to replicate the same rules.

- **Fail2ban Setup**: The Chef cookbook installs and configures fail2ban.
  - Migration approach: Use Ansible Galaxy role `geerlingguy.security` or create a custom role for fail2ban configuration.

- **SSH Hardening**: The Chef cookbook disables root login and password authentication.
  - Migration approach: Use Ansible's `lineinfile` module or the `geerlingguy.security` role to apply the same SSH hardening measures.

- **Vault/secrets management**:
  - Redis password in the cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in the fastapi-tutorial cookbook: User "fastapi" with password "fastapi_password"
  - SSL certificates and private keys generated and stored in `/etc/ssl/certs` and `/etc/ssl/private`
  - Total credentials detected: 3 (Redis password, PostgreSQL username, PostgreSQL password)

### Technical Challenges

- **SSL Certificate Generation**: The Chef cookbook generates self-signed SSL certificates for each site.
  - Mitigation: Create an Ansible role that uses the `openssl_certificate` module to generate self-signed certificates with the same parameters.

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically creates Nginx site configurations based on node attributes.
  - Mitigation: Use Ansible templates and loops to generate site configurations based on variables defined in group_vars or host_vars.

- **Redis Configuration Patching**: The Chef cookbook includes a hack to modify Redis configuration files after they're created.
  - Mitigation: Create a custom Redis template in Ansible that correctly formats the configuration from the start, avoiding post-creation modifications.

- **PostgreSQL User and Database Creation**: The Chef cookbook uses direct shell commands to create PostgreSQL users and databases.
  - Mitigation: Use Ansible's `postgresql_user` and `postgresql_db` modules for more idiomatic database management.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create base Nginx role
   - Implement SSL certificate generation
   - Configure virtual hosts
   - Implement security hardening (firewall, fail2ban)

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Configure Python environment and application deployment
   - Set up systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based distributions.
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA).
3. The security hardening measures (fail2ban, ufw, SSH configuration) are required in the migrated solution.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The Redis and PostgreSQL passwords in the Chef cookbooks are development passwords and will be replaced with more secure values in production.
6. The Vagrant development environment is not critical to migrate, as Ansible can work with various local development solutions.
7. The current Chef setup appears to be for a development/testing environment rather than production, given the self-signed certificates and hardcoded credentials.