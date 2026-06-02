# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope includes three Chef cookbooks with moderate complexity. Based on the analysis, we estimate a 2-3 week timeline for complete migration, with the most complex components being the multi-site Nginx configuration and security hardening.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git-based deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef Solo configuration with run list and node attributes
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ as indicated in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **Firewall Configuration**: Migration of UFW rules to appropriate Ansible firewall module
  - Approach: Use ansible.posix.firewalld or ansible.builtin.ufw module depending on target OS
  
- **Fail2ban Setup**: Convert fail2ban configuration to Ansible
  - Approach: Use community.general.fail2ban module or template-based configuration

- **SSH Hardening**: Migrate SSH security configurations
  - Approach: Use ansible.posix.sshd module or template-based configuration

- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - SSL certificates and private keys in nginx-multisite cookbook
  - Approach: Use Ansible Vault for all credentials and certificate management

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts with SSL
  - Mitigation: Create a custom Ansible role with templates that can handle the same level of flexibility
  
- **SSL Certificate Management**: Self-signed certificate generation and management
  - Mitigation: Use the community.crypto collection for certificate generation and management

- **System Hardening**: Comprehensive security configurations across multiple services
  - Mitigation: Leverage existing Ansible security roles (e.g., dev-sec.os-hardening) and customize as needed

- **Service Orchestration**: Ensuring proper service dependencies and startup order
  - Mitigation: Use Ansible handlers and meta dependencies to ensure proper service ordering

### Migration Order

1. **cache cookbook** (low risk, moderate value)
   - Simple configuration of standard services
   - Few dependencies on other components

2. **nginx-multisite cookbook** (moderate complexity, high value)
   - Core infrastructure component
   - Required for application access
   - Contains security configurations

3. **fastapi-tutorial cookbook** (high complexity, dependencies)
   - Depends on PostgreSQL and potentially the web server
   - Involves application deployment and database configuration

### Assumptions

1. The target environment will continue to use the same operating systems (Fedora/Ubuntu/CentOS)
2. Self-signed certificates are acceptable for development; production would require proper certificate management
3. The current security configurations are appropriate for the target environment
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and Memcached configurations meet performance requirements
6. No custom modules or plugins are required beyond what's visible in the repository
7. No external service dependencies exist beyond what's configured in the cookbooks
8. The current Vagrant development workflow should be preserved in the Ansible migration