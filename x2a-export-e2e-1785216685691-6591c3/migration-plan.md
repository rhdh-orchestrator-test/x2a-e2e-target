# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-service environment consisting of Nginx with multiple SSL-enabled sites, caching services (Redis and Memcached), and a FastAPI application with PostgreSQL database. The migration to Ansible is estimated to be of moderate complexity, requiring approximately 3-4 weeks for a complete migration with testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef Solo configuration file containing the run list and node attributes
- `solo.rb`: Chef Solo Ruby configuration file defining paths and log settings
- `Vagrantfile`: Vagrant configuration for local development using Fedora 42
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used for development in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package module with custom configuration

### Security Considerations

- **SSL/TLS Configuration**: Self-signed certificates are generated for development; migration should maintain this capability while allowing for production certificates
- **Firewall Rules**: UFW configuration must be migrated to appropriate firewall module (ufw or firewalld depending on target OS)
- **fail2ban**: Configuration needs to be migrated to Ansible fail2ban role
- **SSH Hardening**: SSH configuration hardening (disable root login, password authentication) needs to be maintained
- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL database credentials in fastapi-tutorial cookbook: username "fastapi" with password "fastapi_password"
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts with SSL will require careful templating in Ansible
- **Service Dependencies**: Ensuring proper ordering of service deployments (database before application, etc.)
- **OS Compatibility**: The current configuration supports both Ubuntu and CentOS; Ansible playbooks should maintain this compatibility
- **Redis Configuration**: The current Chef cookbook includes a Ruby block to fix Redis configuration files, which will need a custom approach in Ansible

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Begin with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement virtual hosts configuration
   - Add security hardening (fail2ban, firewall)

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (moderate complexity, depends on database)
   - Set up PostgreSQL database
   - Deploy Python application with virtual environment
   - Configure systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/Fedora
2. Self-signed certificates are acceptable for development, but production deployment may require integration with Let's Encrypt or other certificate providers
3. The current security configurations (fail2ban, UFW, SSH hardening) are required in the migrated solution
4. The FastAPI application source will continue to be pulled from the same Git repository
5. The Redis and Memcached configurations do not require significant changes beyond what's currently configured
6. The Vagrant development environment should be maintained but converted to use Ansible provisioning instead of Chef