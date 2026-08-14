# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with FastAPI application backend and caching services (Redis and Memcached). The migration scope is moderate, involving 3 cookbooks with external dependencies. Based on the complexity and number of components, we estimate a 2-3 week timeline for complete migration, including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL setup, security hardening (fail2ban, UFW)

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services (Memcached and Redis) with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines the development environment using Vagrant with Fedora 42
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

Based on the source repository analysis:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Configuration**: Migration must preserve SSL certificate paths and configurations
  - Current paths: /etc/ssl/certs (certificates), /etc/ssl/private (private keys)
  - Migration approach: Use ansible.builtin.copy or ansible.builtin.template modules with proper permissions

- **Fail2ban Configuration**: Security hardening must be maintained
  - Migration approach: Use community.general.fail2ban module or dedicated role

- **UFW Firewall Rules**: Firewall configuration must be preserved
  - Migration approach: Use community.general.ufw module

- **SSH Hardening**: SSH security settings must be maintained
  - Migration approach: Use ansible.posix.ssh_config module

- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: User "fastapi" with password "fastapi_password"
  - Total credentials detected: 2 hardcoded passwords

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically creates multiple Nginx sites with SSL
  - Mitigation: Use Ansible templates with loops to generate site configurations
  - Use ansible.builtin.template module with jinja2 templates similar to the ERB templates

- **Service Dependencies**: The FastAPI application depends on PostgreSQL
  - Mitigation: Use Ansible handlers and meta dependencies to ensure proper service ordering

- **Custom Redis Configuration**: The cache cookbook includes a Ruby block to modify Redis configuration
  - Mitigation: Use Ansible's lineinfile or template module with proper regex handling

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL configuration
   - Add site configurations
   - Add security hardening

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Set up PostgreSQL database
   - Deploy Python application
   - Configure systemd service

### Assumptions

1. The current Chef setup assumes manual SSL certificate generation or provisioning
2. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is publicly accessible
3. The current setup is designed for a single-server deployment rather than distributed services
4. No CI/CD pipeline integration is present in the current configuration
5. The Vagrant environment is primarily for development/testing, not production
6. No monitoring or logging solutions are configured beyond basic service logs
7. No backup strategy is defined for PostgreSQL database or Redis data
8. The current setup does not include load balancing or high availability configurations