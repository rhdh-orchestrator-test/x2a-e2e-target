# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx configuration with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three primary Chef cookbooks to Ansible roles, handling external dependencies, and ensuring proper security configurations are maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3-4 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7-8 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear dependencies
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration

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

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible Galaxy requirements.yml
- `Policyfile.rb`: Chef policy definition - will be replaced by Ansible playbooks
- `solo.rb`: Chef Solo configuration - will be replaced by Ansible configuration
- `solo.json`: Node attributes and run list - will be replaced by Ansible inventory and variables
- `Vagrantfile`: Development environment definition - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible provisioning

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.general.nginx or builtin package module
- **memcached (~> 6.0)**: Replace with Ansible community.general.memcached or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible community.redis or custom role
- **ssl_certificate (~> 2.1)**: Replace with Ansible community.crypto modules for certificate management

### Security Considerations

- **SSL Certificate Management**: Migration must maintain proper permissions (640) and ownership (root:ssl-cert) for private keys
- **Firewall Configuration**: UFW rules must be migrated to equivalent Ansible UFW module configurations
- **Fail2ban Setup**: Configuration must be preserved in Ansible format
- **SSH Hardening**: Settings for disabling root login and password authentication must be maintained
- **Redis Authentication**: Password must be securely managed (consider Ansible Vault)
- **PostgreSQL Credentials**: Database credentials should be stored securely (Ansible Vault)

### Technical Challenges

- **Multi-site Nginx Configuration**: Ensure the dynamic generation of site configurations is properly implemented in Ansible
- **SSL Certificate Generation**: Ensure self-signed certificates are generated with proper permissions and security
- **Service Dependencies**: Maintain proper ordering of service deployments (e.g., PostgreSQL before FastAPI application)
- **Python Environment Management**: Ensure proper setup of Python virtual environments and dependency installation
- **Security Hardening**: Ensure all security measures are properly implemented in Ansible

### Migration Order

1. **cache role** (low complexity, foundational service)
   - Implement Memcached configuration
   - Implement Redis with authentication

2. **nginx-multisite role** (medium complexity, depends on proper SSL handling)
   - Implement base Nginx configuration
   - Implement SSL certificate generation
   - Implement site configuration templates
   - Implement security hardening (fail2ban, UFW)

3. **fastapi-tutorial role** (high complexity, depends on database)
   - Implement PostgreSQL database setup
   - Implement Python environment configuration
   - Implement application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions (Ubuntu 18.04+, CentOS 7+)
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA)
3. The current security configurations are appropriate and should be maintained
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. Redis and PostgreSQL passwords in the Chef recipes are placeholders and will be replaced with secure passwords in Ansible Vault
6. The Vagrant development environment will be maintained for testing the Ansible roles

## Implementation Strategy

### 1. Project Structure

Create an Ansible project with the following structure:

```
ansible-nginx-multisite/
├── inventories/
│   ├── development/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   └── production/
│       ├── hosts.yml
│       └── group_vars/
├── roles/
│   ├── nginx-multisite/
│   ├── cache/
│   └── fastapi-tutorial/
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
├── requirements.yml
└── Vagrantfile
```

### 2. Dependency Management

Create a `requirements.yml` file to manage external role dependencies:

```yaml
---
collections:
  - name: community.general
  - name: community.crypto
  - name: community.postgresql
```

### 3. Variable Management

Convert Chef attributes to Ansible variables, using group_vars and host_vars as appropriate.

### 4. Testing Strategy

Maintain the Vagrant setup for testing, but adapt it to use Ansible provisioning instead of Chef.

### 5. Documentation

Create comprehensive documentation for each role, including:
- Role purpose and functionality
- Required variables
- Dependencies
- Example usage