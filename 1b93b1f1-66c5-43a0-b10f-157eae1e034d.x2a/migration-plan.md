# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx configuration with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Moderate number of external dependencies (nginx, memcached, redisio)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
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
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible Galaxy requirements.yml
- `Policyfile.rb`: Chef policy definition - will be replaced by Ansible playbook structure
- `solo.rb`: Chef Solo configuration - will be replaced by Ansible configuration
- `solo.json`: Node attributes and run list - will be replaced by Ansible inventory and variables
- `Vagrantfile`: VM configuration for development/testing - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible provisioning

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management tasks

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migrate to Ansible's crypto modules for certificate generation or consider integrating with Let's Encrypt.
- **Firewall Configuration (UFW)**: Migrate UFW rules to Ansible's ufw module or firewalld for Fedora/RHEL systems.
- **fail2ban Configuration**: Migrate fail2ban configuration to Ansible's template module.
- **SSH Hardening**: Migrate SSH security configurations using Ansible's lineinfile or template modules.
- **Redis Authentication**: Ensure secure password handling using Ansible Vault for the Redis password.
- **PostgreSQL Authentication**: Secure database credentials using Ansible Vault.

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of Nginx site configurations based on node attributes will need careful translation to Ansible's template system.
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be replicated in Ansible.
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations (e.g., PostgreSQL before FastAPI application).
- **Platform Compatibility**: Ensuring compatibility across both Debian/Ubuntu and RHEL/CentOS/Fedora systems.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Base Nginx installation
   - SSL certificate generation
   - Virtual host configuration
   - Security hardening

2. **cache** (low complexity, independent service)
   - Memcached configuration
   - Redis installation and configuration

3. **fastapi-tutorial** (high complexity, depends on database)
   - PostgreSQL installation and configuration
   - Python environment setup
   - Application deployment
   - Service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or similar Linux distributions.
2. Self-signed certificates are acceptable for development/testing; production may require proper CA-signed certificates.
3. The security requirements (fail2ban, UFW, SSH hardening) will remain the same.
4. The FastAPI application source code will be available at the same GitHub repository.
5. The Redis password and PostgreSQL credentials will need to be securely managed in the new Ansible setup.
6. The Nginx site configurations (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same.

## Ansible Structure Recommendation

```
ansible-nginx-multisite/
├── inventories/
│   ├── development/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   │       └── all.yml
│   └── production/
│       ├── hosts.yml
│       └── group_vars/
│           └── all.yml
├── roles/
│   ├── nginx_multisite/
│   │   ├── defaults/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   │   ├── main.yml
│   │   │   ├── install.yml
│   │   │   ├── ssl.yml
│   │   │   ├── security.yml
│   │   │   └── sites.yml
│   │   └── templates/
│   ├── cache_services/
│   │   ├── defaults/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   │   ├── main.yml
│   │   │   ├── memcached.yml
│   │   │   └── redis.yml
│   │   └── templates/
│   └── fastapi_app/
│       ├── defaults/
│       ├── handlers/
│       ├── tasks/
│       │   ├── main.yml
│       │   ├── postgresql.yml
│       │   └── app.yml
│       └── templates/
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
├── requirements.yml
└── vagrant.yml
```

## Implementation Notes

1. **Variable Management**:
   - Move from Chef node attributes to Ansible variables
   - Use group_vars and host_vars for environment-specific configurations
   - Use Ansible Vault for sensitive information (Redis password, PostgreSQL credentials)

2. **Template Conversion**:
   - Convert ERB templates to Jinja2 format
   - Adapt template logic to Ansible's template module

3. **Idempotency**:
   - Ensure all tasks are idempotent, similar to the Chef recipes
   - Use Ansible's state management for packages, services, and files

4. **Testing Strategy**:
   - Adapt the Vagrant setup for testing Ansible roles
   - Implement molecule tests for individual roles
   - Create integration tests for the complete setup

5. **Documentation**:
   - Document each role with README files
   - Include examples for common customizations
   - Document the migration process for knowledge transfer