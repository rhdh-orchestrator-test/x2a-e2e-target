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
- The Chef cookbooks are well-structured and follow standard patterns
- Security configurations are comprehensive but straightforward
- External dependencies on community cookbooks will need Ansible Galaxy equivalents

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
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio, ssl_certificate)
- `Policyfile.rb`: Chef Policyfile defining the run list and cookbook dependencies
- `Vagrantfile`: Defines the development VM environment using Fedora 42
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `solo.json`: Configuration data for Chef Solo, including site configurations and security settings
- `solo.rb`: Chef Solo configuration file

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) based on cookbook metadata, with development environment using Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or use the `ansible.builtin.package` module with templates
- **memcached (~> 6.0)**: Use Ansible Galaxy's `geerlingguy.memcached` role or create a custom role
- **redisio (~> 7.2.4)**: Use Ansible Galaxy's `geerlingguy.redis` role or create a custom role
- **ssl_certificate (~> 2.1)**: Use Ansible's `openssl_*` modules for certificate management

### Security Considerations

- **Firewall (UFW)**: Migrate to Ansible's `ufw` module or `firewalld` module depending on target OS
- **fail2ban**: Use Ansible Galaxy's `fail2ban` role or create a custom role with templates
- **SSH hardening**: Use Ansible's `lineinfile` module to modify SSH configuration
- **SSL certificates**: Use Ansible's `openssl_*` modules for self-signed certificates or `community.crypto` collection
- **Redis password**: Store in Ansible Vault and reference in templates
- **PostgreSQL credentials**: Store database credentials in Ansible Vault

### Technical Challenges

- **Multi-site configuration**: Create a flexible Ansible role that can handle multiple site configurations from variables
- **Self-signed certificates**: Ensure proper certificate generation and permissions in Ansible
- **Service dependencies**: Maintain proper ordering of service installation and configuration
- **Idempotency**: Ensure all operations are idempotent, especially database user creation and certificate generation

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Create base Nginx role
   - Add SSL certificate handling
   - Add virtual host configuration
   - Add security hardening

2. **cache** (low complexity, standalone services)
   - Create Memcached role
   - Create Redis role with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Create PostgreSQL role
   - Create Python application deployment role
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Linux-based (Ubuntu/CentOS/Fedora)
2. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or other CA)
3. The same directory structure for web content will be maintained
4. The FastAPI application source will continue to be pulled from the same Git repository
5. Redis and PostgreSQL passwords in the Chef recipes are placeholders and will be replaced with secure values in Ansible Vault
6. The Vagrant development environment will be maintained but converted to use Ansible provisioner

## Ansible Structure Recommendation

```
ansible-nginx-multisite/
├── inventories/
│   ├── development/
│   │   ├── group_vars/
│   │   │   └── all.yml  # Development environment variables
│   │   └── hosts        # Development inventory
│   └── production/
│       ├── group_vars/
│       │   └── all.yml  # Production environment variables
│       └── hosts        # Production inventory
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   └── templates/
│   ├── ssl/
│   ├── security/
│   ├── memcached/
│   ├── redis/
│   ├── postgresql/
│   └── fastapi/
├── playbooks/
│   ├── site.yml         # Main playbook
│   ├── nginx.yml        # Nginx-specific playbook
│   ├── cache.yml        # Cache services playbook
│   └── fastapi.yml      # FastAPI application playbook
├── Vagrantfile          # For development testing
├── ansible.cfg          # Ansible configuration
└── requirements.yml     # Ansible Galaxy requirements
```

## Security and Secrets Management

1. Create an Ansible Vault for sensitive information:
   - Redis authentication password
   - PostgreSQL database credentials
   - Any API keys or tokens

2. Implement proper file permissions for SSL certificates and private keys

3. Maintain the security hardening features from the original Chef cookbooks:
   - SSH hardening (disable root login, password authentication)
   - Firewall configuration (UFW)
   - fail2ban for intrusion prevention
   - System hardening via sysctl parameters

## Testing Strategy

1. Create a testing pipeline using Molecule for individual role testing
2. Maintain the Vagrant environment for integration testing
3. Implement idempotence tests to ensure playbooks can be run multiple times
4. Create verification tests to confirm services are running correctly after provisioning