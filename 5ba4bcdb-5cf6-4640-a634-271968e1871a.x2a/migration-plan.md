# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and preserving security configurations.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3-4 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 6-8 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration
- Self-contained application deployment

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
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `Policyfile.rb`: Chef policy file defining the run list and cookbook dependencies
- `Vagrantfile`: VM configuration for development and testing
- `vagrant-provision.sh`: Provisioning script for Vagrant VM setup
- `solo.json`: Configuration data for Chef solo runs
- `solo.rb`: Chef solo configuration file

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata files. The Vagrantfile uses Fedora 42 for development.
- **Virtual Machine Technology**: Vagrant with libvirt provider as indicated in the Vagrantfile
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `ansible.posix.nginx`)
- **ssl_certificate (~> 2.1)**: Replace with Ansible's `community.crypto` collection for certificate management
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: Migration must preserve the self-signed certificate generation for development environments
- **Firewall Configuration**: UFW rules need to be migrated to equivalent Ansible UFW module tasks
- **Fail2ban Setup**: Configuration needs to be preserved in Ansible tasks
- **SSH Hardening**: SSH security configurations (disabling root login, password authentication) need to be maintained
- **Redis Authentication**: Redis password must be securely managed in Ansible Vault
- **PostgreSQL Authentication**: Database credentials need to be securely stored in Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of site configurations based on attributes needs careful translation to Ansible variables and templates
- **SSL Certificate Management**: Ensuring proper permissions and security for SSL certificates and private keys
- **Service Dependencies**: Maintaining the correct order of service deployment (database before application, etc.)
- **Python Environment Management**: Properly setting up Python virtual environments and dependencies
- **Security Hardening**: Ensuring all security measures are properly implemented in Ansible

### Migration Order

1. **cache cookbook** (Low complexity, foundational service)
   - Implement Redis and Memcached configuration
   - Set up authentication and security

2. **nginx-multisite cookbook** (Medium complexity, core infrastructure)
   - Implement base Nginx configuration
   - Set up SSL certificate generation
   - Configure multi-site setup
   - Implement security hardening

3. **fastapi-tutorial cookbook** (High complexity, application layer)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service
   - Integrate with Nginx

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS as specified in the cookbook metadata
2. Self-signed certificates are acceptable for development environments
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The current security configurations are appropriate for the target environment
5. The Redis password and PostgreSQL credentials in the Chef recipes are development values and will be replaced with secure values in production
6. The Nginx site configurations (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same in the target environment

## Ansible Structure Recommendation

```
ansible-project/
├── inventories/
│   ├── development/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   └── production/
│       ├── hosts.yml
│       └── group_vars/
├── roles/
│   ├── nginx_multisite/
│   │   ├── defaults/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   ├── templates/
│   │   └── files/
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
└── group_vars/
    ├── all/
    │   ├── vars.yml
    │   └── vault.yml
    └── webservers/
        ├── vars.yml
        └── vault.yml
```

## Testing Strategy

1. Develop Vagrant-based testing environment similar to the existing setup
2. Create molecule tests for each Ansible role
3. Implement integration tests to verify the complete stack
4. Validate security configurations with appropriate scanning tools
5. Perform idempotency tests to ensure roles can be run multiple times without issues

## Documentation Requirements

1. README for each Ansible role explaining its purpose and configuration options
2. Variable documentation for all configurable parameters
3. Example playbooks for common deployment scenarios
4. Security considerations and best practices
5. Troubleshooting guide for common issues