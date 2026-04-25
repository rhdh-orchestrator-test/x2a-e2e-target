# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the multi-site configuration and security considerations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file containing node attributes and run list
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration file for local development environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development or on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy or custom role

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration should maintain proper permissions (640) and ownership (root:ssl-cert)
  - Consider integrating with Ansible Vault for certificate storage

- **Firewall Configuration**: 
  - UFW configuration needs to be migrated to equivalent Ansible UFW module
  - Maintain default deny policy with specific allow rules for SSH, HTTP, and HTTPS

- **Fail2ban Integration**:
  - Migrate fail2ban configuration to Ansible
  - Maintain jail configuration for SSH and web services

- **SSH Hardening**:
  - Maintain root login disable configuration
  - Maintain password authentication disable configuration

- **Vault/secrets management**:
  - Redis password in cache cookbook (plaintext: "redis_secure_password_123")
  - PostgreSQL user and password in fastapi-tutorial cookbook (plaintext: "fastapi_password")
  - Environment variables in .env file for FastAPI application
  - Total credentials detected: 3 (all hardcoded in recipes)

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Maintaining the dynamic generation of multiple virtual hosts with SSL
  - Mitigation: Use Ansible templates with loops to generate site configurations

- **SSL Certificate Generation**:
  - Challenge: Replicating the self-signed certificate generation logic
  - Mitigation: Use Ansible's openssl_certificate module with proper permission handling

- **Service Orchestration**:
  - Challenge: Ensuring proper service restart only when configuration changes
  - Mitigation: Use Ansible handlers and notify mechanism

- **Database User and Schema Creation**:
  - Challenge: PostgreSQL user and database creation with proper permissions
  - Mitigation: Use Ansible's postgresql_user and postgresql_db modules

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add virtual host configuration
   - Add security hardening (fail2ban, firewall, headers)

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database and user
   - Deploy application code from Git
   - Configure Python environment and dependencies
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile)
2. The same directory structure for web document roots will be maintained
3. Self-signed certificates are acceptable for the migrated environment (no Let's Encrypt integration required)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current plaintext secrets in the Chef recipes will be migrated to Ansible Vault
6. The same network configuration (ports, IP addresses) will be maintained
7. No additional monitoring or logging solutions beyond what's in the current Chef setup will be required
8. The Vagrant development environment will be maintained but converted to use Ansible provisioner