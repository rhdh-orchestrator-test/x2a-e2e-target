# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, security configurations, and service deployments.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7 weeks

**Complexity Assessment:** Medium
- Multiple interconnected services
- Security configurations
- SSL certificate management
- Database setup and configuration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup with self-signed certificates, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing both local cookbooks and external dependencies from Chef Supermarket
  - Migration considerations: Dependencies need to be mapped to Ansible Galaxy roles or custom roles
  
- `solo.json`: Chef configuration file containing the run list and node attributes
  - Migration considerations: Convert to Ansible inventory variables or group_vars

- `solo.rb`: Chef configuration file specifying paths and log settings
  - Migration considerations: Replace with Ansible configuration

- `Vagrantfile`: Defines the development VM using Fedora 42
  - Migration considerations: Update to use Ansible provisioner instead of Chef

- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks
  - Migration considerations: Replace with Ansible installation and playbook execution

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in the Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.general.nginx or custom Nginx role
- **memcached (~> 6.0)**: Replace with geerlingguy.memcached or custom Memcached role
- **redisio (~> 7.2.4)**: Replace with geerlingguy.redis or custom Redis role
- **PostgreSQL**: Replace with geerlingguy.postgresql or community.postgresql collection

### Security Considerations

- **SSL/TLS Configuration**: 
  - Self-signed certificate generation needs to be migrated
  - Secure TLS protocols and ciphers configuration
  - Migration approach: Use Ansible crypto modules for certificate generation

- **Firewall Configuration**: 
  - UFW rules for HTTP, HTTPS, and SSH
  - Migration approach: Use Ansible UFW module or firewalld module depending on target OS

- **Fail2ban Integration**:
  - Migration approach: Use community.general.fail2ban module or custom role

- **System Hardening**:
  - Sysctl security settings
  - SSH hardening (disable root login, password authentication)
  - Migration approach: Use ansible-hardening role or dev-sec.os-hardening

- **Vault/secrets management**:
  - Redis password in plaintext in recipe
  - PostgreSQL credentials in plaintext in recipe
  - Migration approach: Use Ansible Vault for sensitive data

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically generates Nginx site configurations based on node attributes
  - Mitigation strategy: Use Ansible templates with similar logic, leveraging host_vars or group_vars

- **SSL Certificate Management**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation strategy: Use Ansible crypto modules or consider integrating with Let's Encrypt for production

- **Database Initialization**: 
  - Description: PostgreSQL database and user creation is handled via shell commands
  - Mitigation strategy: Use Ansible PostgreSQL modules for idempotent database management

- **Service Orchestration**: 
  - Description: Multiple interdependent services need to be configured in the right order
  - Mitigation strategy: Use Ansible handlers and proper task dependencies

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL/TLS management
   - Implement security configurations (fail2ban, UFW)
   - Configure virtual hosts

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on other services)
   - Set up PostgreSQL database
   - Deploy Python application
   - Configure systemd service
   - Integrate with Nginx

### Assumptions

1. The target environment will continue to be either Ubuntu (>= 18.04) or CentOS (>= 7.0)
2. The Vagrant development environment will be maintained for testing
3. Self-signed certificates are acceptable for development, but production may require proper certificates
4. The current security configurations are appropriate and should be maintained
5. The FastAPI application source will continue to be pulled from the same Git repository
6. Redis and PostgreSQL passwords in the current configuration are development passwords and will be replaced with proper secrets management
7. The current Nginx site configurations (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same
8. No additional services beyond what's currently configured will be needed