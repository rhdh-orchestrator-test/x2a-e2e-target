# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three primary Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration
- Self-contained environment with Vagrant for testing

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, ssl_certificate, memcached, redisio)
- `Policyfile.rb`: Chef Policyfile defining the run list and cookbook dependencies
- `Vagrantfile`: VM configuration for testing with Fedora 42
- `vagrant-provision.sh`: Provisioning script for Chef setup in Vagrant
- `solo.json`: Node attributes configuration for Chef Solo
- `solo.rb`: Chef Solo configuration file

### Target Details

Based on the source configuration files:

- **Operating System**: Supports Ubuntu 18.04+ and CentOS 7.0+ (based on cookbook metadata), with Fedora 42 used in Vagrant for testing
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management using openssl_* modules

### Security Considerations

- **SSL Certificate Management**: Migration of self-signed certificate generation for multiple domains
- **Firewall Configuration**: UFW rules need to be migrated to equivalent Ansible UFW module tasks
- **Fail2ban Setup**: Configuration needs to be migrated to Ansible tasks
- **SSH Hardening**: SSH configuration hardening (disable root login, password authentication)
- **Redis Authentication**: Secure password for Redis needs to be managed (currently hardcoded)
- **PostgreSQL Authentication**: Database credentials need secure management (currently hardcoded)

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of multiple Nginx site configurations needs careful translation to Ansible templates
- **SSL Certificate Management**: Self-signed certificate generation for multiple domains needs to be handled properly
- **Security Hardening**: Comprehensive security measures need to be maintained during migration
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Implement site configuration templates
   - Add security hardening features

2. **cache** (low complexity, standalone services)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Set up PostgreSQL database
   - Configure Python environment
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The target environment will continue to support the same operating systems (Ubuntu 18.04+, CentOS 7.0+)
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA)
3. The hardcoded passwords in the Chef recipes will be replaced with Ansible Vault or another secret management solution
4. The FastAPI application source will continue to be available at the specified Git repository
5. The Vagrant testing environment will be maintained but updated to use Ansible provisioning

## Ansible Structure Recommendation

```
ansible/
├── inventories/
│   ├── development/
│   │   ├── group_vars/
│   │   │   ├── all.yml
│   │   │   └── web_servers.yml
│   │   └── hosts.yml
│   └── production/
├── roles/
│   ├── nginx_multisite/
│   │   ├── defaults/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   └── templates/
│   ├── cache_services/
│   │   ├── defaults/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   └── templates/
│   └── fastapi_app/
│       ├── defaults/
│       ├── handlers/
│       ├── tasks/
│       └── templates/
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
└── vagrant/
    ├── Vagrantfile
    └── ansible_provision.sh
```

## Migration Testing Strategy

1. Develop Ansible roles individually with isolated testing
2. Create a Vagrant environment similar to the existing one but using Ansible provisioning
3. Test each role in isolation, then test the complete playbook
4. Verify functionality matches the original Chef implementation:
   - Nginx sites are properly configured with SSL
   - Security hardening is in place
   - Caching services are running and configured correctly
   - FastAPI application is deployed and accessible

## Knowledge Transfer Plan

1. Document each Ansible role with detailed README files
2. Create a migration summary document highlighting key differences between the Chef and Ansible implementations
3. Provide example commands and usage patterns for common operations
4. Schedule knowledge transfer sessions with the team