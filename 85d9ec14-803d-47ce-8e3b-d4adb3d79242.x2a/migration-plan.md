# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Multiple interconnected services
- Security configurations that need careful migration
- External cookbook dependencies that need Ansible equivalents

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and custom site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, ssl_certificate, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `Policyfile.rb`: Defines the run list and cookbook versions - will be replaced by Ansible playbook structure
- `solo.json`: Contains node configuration data - will be migrated to Ansible inventory variables
- `solo.rb`: Chef Solo configuration - not needed in Ansible
- `Vagrantfile`: VM configuration for testing - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible playbook

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., geerlingguy.redis)
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management tasks or community role

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability while allowing for future integration with Let's Encrypt or other certificate authorities.
- **Fail2ban Configuration**: Security hardening with fail2ban needs to be preserved in the Ansible implementation.
- **UFW Firewall Rules**: Current firewall rules need to be migrated to equivalent Ansible UFW tasks.
- **SSH Hardening**: SSH security configurations (disable root login, password authentication) need to be maintained.
- **Redis Authentication**: Redis is configured with password authentication which must be preserved.
- **PostgreSQL Security**: Database user creation with password needs secure handling in Ansible.

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of multiple Nginx site configurations needs to be replicated in Ansible using templates and loops.
- **Service Interdependencies**: The FastAPI application depends on PostgreSQL, and the web server depends on the application being available. These dependencies need to be managed in Ansible.
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be replicated in Ansible.
- **System Hardening**: The comprehensive security configurations need careful migration to maintain security posture.

### Migration Order

1. **nginx-multisite cookbook** (moderate complexity, foundation for other services)
   - Create Ansible role for Nginx installation and configuration
   - Implement virtual host configuration with SSL support
   - Migrate security hardening configurations

2. **cache cookbook** (low complexity, independent service)
   - Create Ansible roles for Memcached and Redis
   - Configure Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial cookbook** (high complexity, depends on database)
   - Create Ansible role for PostgreSQL
   - Create Ansible role for FastAPI application deployment
   - Implement Python environment setup and application configuration
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile).
2. Self-signed certificates are acceptable for the migrated solution (production environments might require integration with proper certificate authorities).
3. The security requirements (fail2ban, ufw, SSH hardening) will remain the same in the new implementation.
4. The FastAPI application source will continue to be available at the specified Git repository.
5. The Redis password and PostgreSQL credentials in the Chef recipes are development/testing credentials and will be replaced with proper secret management in production Ansible deployments.
6. The Nginx site configurations (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same in the migrated solution.