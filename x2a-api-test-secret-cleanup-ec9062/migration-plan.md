# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3-4 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 6-8 weeks

**Complexity Assessment:** Medium to High
- Multiple interconnected services
- Security configurations that need careful migration
- SSL certificate management
- Database integration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, fail2ban integration, UFW firewall rules, security headers

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `Vagrantfile`: Defines development environment using Fedora 42, with port forwarding and networking configuration
- `solo.json`: Defines Chef run list and node attributes including nginx site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in the Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection
- **memcached (~> 6.0)**: Replace with Ansible memcached role
- **redisio (~> 7.2.4)**: Replace with Ansible redis role
- **PostgreSQL**: Replace with Ansible postgresql role
- **Python/venv**: Replace with Ansible pip and Python modules

### Security Considerations

- **SSL/TLS Configuration**: 
  - Migration approach: Use Ansible crypto modules for certificate generation
  - Ensure proper permissions on private keys (0640) and ownership (root:ssl-cert)

- **Firewall Rules (UFW)**:
  - Migration approach: Use Ansible ufw module to configure firewall rules
  - Ensure SSH, HTTP, and HTTPS ports remain accessible

- **fail2ban Integration**:
  - Migration approach: Use Ansible to deploy and configure fail2ban
  - Maintain existing jail configurations

- **SSH Hardening**:
  - Migration approach: Use Ansible ssh_config module to disable root login and password authentication
  - Ensure these security settings are maintained during migration

- **Vault/secrets management**:
  - Redis password: Currently hardcoded as 'redis_secure_password_123' in the cache cookbook
  - PostgreSQL credentials: Hardcoded as user 'fastapi' with password 'fastapi_password'
  - Count: 2 sets of credentials detected
  - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically generates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible templates with similar logic to generate site configurations

- **SSL Certificate Management**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible crypto modules to generate certificates or integrate with Let's Encrypt

- **Service Orchestration**: 
  - Description: Services have dependencies (FastAPI depends on PostgreSQL, Nginx depends on SSL certificates)
  - Mitigation: Use Ansible handlers and proper task ordering to ensure dependencies are met

- **Security Hardening**: 
  - Description: Multiple security layers (fail2ban, UFW, SSH hardening, SSL configuration)
  - Mitigation: Create dedicated security role with separate tasks for each component

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Begin with basic Nginx installation and configuration
   - Add SSL certificate management
   - Implement virtual hosts configuration
   - Add security hardening features

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (high complexity, depends on database)
   - Set up PostgreSQL database
   - Deploy FastAPI application from Git
   - Configure Python environment and dependencies
   - Set up systemd service

### Assumptions

1. The target environment will continue to support the same operating systems (Ubuntu 18.04+ or CentOS 7.0+)
2. The same network architecture will be maintained
3. Self-signed certificates are acceptable for development/testing (production would likely use proper certificates)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current security requirements (fail2ban, UFW, SSH hardening) will be maintained
6. The Vagrant development environment will be replaced with an equivalent Ansible-based setup
7. Redis and PostgreSQL passwords will be managed more securely in the Ansible implementation
8. The current directory structure for web content (/var/www/[site]) will be maintained