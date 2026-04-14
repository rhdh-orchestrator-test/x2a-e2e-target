# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and preserving security configurations.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3-4 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7-8 weeks

**Complexity Assessment:** Medium
- Multiple interconnected services
- Security configurations that need careful migration
- Database and application deployment

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

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

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, ssl_certificate, memcached, redisio)
- `Policyfile.rb`: Chef policy file defining the run list and cookbook dependencies
- `solo.rb`: Chef Solo configuration file
- `solo.json`: Node attributes and run list configuration
- `Vagrantfile`: Vagrant configuration for development/testing environment using Fedora 42
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `ansible.posix.nginx`)
- **ssl_certificate (~> 2.1)**: Replace with Ansible's `community.crypto` collection for certificate management
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: Currently using self-signed certificates; maintain this approach or integrate with Let's Encrypt using Ansible's `community.crypto` collection
- **Firewall Configuration**: UFW configuration needs to be migrated to appropriate firewall module (ufw or firewalld depending on target OS)
- **fail2ban**: Configuration needs to be migrated to Ansible tasks
- **SSH Hardening**: Current configuration disables root login and password authentication; preserve these security settings
- **Redis Authentication**: Redis is configured with password authentication; ensure this is maintained
- **PostgreSQL Security**: Database credentials are currently hardcoded; consider using Ansible Vault for secure storage

### Technical Challenges

- **Multi-OS Support**: The current Chef cookbooks support both Ubuntu and CentOS; Ansible playbooks should maintain this compatibility using OS-specific tasks
- **Service Orchestration**: The current setup has interdependent services (Nginx, Redis, Memcached, PostgreSQL, FastAPI); ensure proper ordering in Ansible
- **SSL Certificate Generation**: Self-signed certificate generation needs to be replicated in Ansible
- **Configuration Templates**: Multiple configuration templates need to be converted from ERB to Jinja2 format

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation
   - Add SSL certificate generation
   - Configure virtual hosts
   - Implement security hardening

2. **cache** (low complexity, standalone services)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/Fedora
2. Self-signed certificates are acceptable for development/testing
3. The same security policies should be maintained in the Ansible implementation
4. The FastAPI application source will continue to be pulled from the same Git repository
5. Redis and Memcached configurations will remain largely unchanged
6. The current directory structure in the target environment (`/opt/fastapi-tutorial`, `/var/www/` for sites) will be maintained
7. The Vagrant development environment will be migrated to use Ansible provisioning instead of Chef
8. No CI/CD pipeline integration is required as part of the migration
9. The current hardcoded credentials will be replaced with Ansible Vault or similar secure storage
10. The migration will not involve changes to the application code or database schema