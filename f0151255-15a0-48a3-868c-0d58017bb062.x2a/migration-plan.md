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

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `Policyfile.rb`: Chef policy file defining the run list and cookbook dependencies
- `Vagrantfile`: Defines the development VM configuration using Vagrant
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `solo.json`: Configuration data for Chef Solo, contains site configurations and security settings
- `solo.rb`: Chef Solo configuration file

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata. The Vagrantfile uses Fedora 42 for development.
- **Virtual Machine Technology**: Vagrant with libvirt provider as indicated in the Vagrantfile
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `ansible.posix.nginx`)
- **ssl_certificate (~> 2.1)**: Replace with Ansible's `community.crypto` collection for certificate management
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: Migration must preserve the self-signed certificate generation for development environments
- **Firewall Configuration**: UFW rules need to be migrated to equivalent Ansible UFW module tasks
- **fail2ban Configuration**: Configuration needs to be migrated to Ansible tasks
- **SSH Hardening**: SSH security configurations (disabling root login, password authentication) need to be preserved
- **Redis Authentication**: Redis password must be securely managed in Ansible Vault
- **PostgreSQL Credentials**: Database credentials should be stored in Ansible Vault

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of multiple Nginx site configurations needs careful translation to Ansible templates
- **SSL Certificate Management**: Self-signed certificate generation logic needs to be preserved
- **Security Hardening**: Comprehensive security measures need to be maintained across the migration
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation
   - Add SSL certificate management
   - Implement site configuration templates
   - Add security hardening features

2. **cache** (low complexity, standalone services)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Set up PostgreSQL database
   - Configure Python environment
   - Deploy application code
   - Set up systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS as specified in the cookbook metadata
2. Self-signed certificates are acceptable for development environments
3. The same security policies (fail2ban, UFW, SSH hardening) will be maintained
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. Redis and PostgreSQL passwords in the Chef recipes are development credentials and will be replaced with secure values in production

## Ansible Structure Recommendation

```
ansible-nginx-multisite/
├── inventories/
│   ├── development/
│   │   ├── group_vars/
│   │   │   ├── all.yml          # Common variables
│   │   │   └── web_servers.yml  # Web server specific variables
│   │   └── hosts                # Development inventory
│   └── production/
│       ├── group_vars/
│       │   ├── all.yml
│       │   └── web_servers.yml
│       └── hosts                # Production inventory
├── roles/
│   ├── nginx_multisite/         # Migrated from nginx-multisite cookbook
│   │   ├── defaults/
│   │   ├── files/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   ├── templates/
│   │   └── vars/
│   ├── cache_services/          # Migrated from cache cookbook
│   │   ├── defaults/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   ├── templates/
│   │   └── vars/
│   └── fastapi_app/             # Migrated from fastapi-tutorial cookbook
│       ├── defaults/
│       ├── handlers/
│       ├── tasks/
│       ├── templates/
│       └── vars/
├── playbooks/
│   ├── site.yml                 # Main playbook
│   ├── nginx.yml                # Nginx specific playbook
│   ├── cache.yml                # Cache services playbook
│   └── fastapi.yml              # FastAPI application playbook
├── group_vars/
│   └── all/
│       ├── vars.yml             # Common variables
│       └── vault.yml            # Encrypted sensitive data
└── vagrant/
    └── Vagrantfile              # For development testing
```

## Security and Secrets Management

All sensitive information found in the Chef recipes should be migrated to Ansible Vault:

1. Redis password: "redis_secure_password_123"
2. PostgreSQL credentials: "fastapi" / "fastapi_password"

## Testing Strategy

1. Develop a parallel Vagrant environment for Ansible to match the existing Chef setup
2. Create test cases for each component:
   - Nginx site accessibility
   - SSL certificate validation
   - Redis authentication
   - FastAPI application functionality
3. Compare outputs and configurations between Chef and Ansible deployments

## Knowledge Transfer Plan

1. Document each Ansible role with detailed README files
2. Create a migration guide for team members
3. Conduct a workshop on the new Ansible structure
4. Pair programming sessions during initial deployment