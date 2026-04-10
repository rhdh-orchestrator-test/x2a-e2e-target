# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has well-structured Chef cookbooks with clear dependencies
- Security configurations need careful migration
- Multiple services with interdependencies require coordinated testing

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio, ssl_certificate) - will be replaced by Ansible Galaxy requirements
- `Policyfile.rb`: Defines the run list and cookbook versions - will be replaced by Ansible playbook structure
- `solo.rb`: Chef Solo configuration - will be replaced by Ansible configuration
- `solo.json`: Node attributes and run list - will be replaced by Ansible inventory variables
- `Vagrantfile`: VM configuration for development/testing - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible provisioning

### Target Details

- **Operating System**: 
  - Primary: Fedora 42 (from Vagrantfile)
  - Also supports: Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation and configuration
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation and configuration
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management tasks or community roles

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability while allowing for integration with Let's Encrypt or other certificate authorities.
- **Firewall Configuration**: UFW configuration needs to be migrated, considering that different distributions may use different firewall tools (firewalld on Fedora/RHEL).
- **Fail2ban Configuration**: Fail2ban setup needs to be migrated with appropriate jails.
- **SSH Hardening**: SSH security configurations (disabling root login, password authentication) need to be preserved.
- **Redis Authentication**: Redis password authentication must be securely migrated.
- **PostgreSQL Authentication**: Database credentials need to be securely managed in Ansible Vault.

### Technical Challenges

- **Multi-platform Support**: The current cookbooks support both Debian/Ubuntu and RHEL/CentOS. Ansible roles should maintain this compatibility.
- **Service Orchestration**: The interdependencies between services (Nginx, Redis, Memcached, PostgreSQL, FastAPI) need to be carefully managed in the Ansible playbook flow.
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be replicated in Ansible.
- **Configuration Templates**: Nginx configuration templates need to be converted to Ansible templates while maintaining the same functionality.
- **System Tuning**: Security-related sysctl configurations need to be properly migrated.

### Migration Order

1. **cache cookbook** (Low complexity, foundational service)
   - Implement Memcached configuration
   - Implement Redis with authentication

2. **nginx-multisite cookbook** (Medium complexity, depends on SSL certificates)
   - Implement basic Nginx installation and configuration
   - Implement SSL certificate generation
   - Implement virtual host configuration
   - Implement security hardening (fail2ban, firewall)

3. **fastapi-tutorial cookbook** (High complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to support both Debian/Ubuntu and RHEL/CentOS families.
2. Self-signed certificates are acceptable for development/testing, but production may require integration with proper certificate authorities.
3. The security requirements (fail2ban, firewall, SSH hardening) will remain the same.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current Redis and PostgreSQL passwords are for development only and will be replaced with secure passwords in production.
6. The Vagrant setup is primarily for development/testing and may not reflect the actual production environment.
7. No custom Ohai plugins or Chef handlers are in use that would require special handling.