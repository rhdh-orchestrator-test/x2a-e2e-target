# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx configuration with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration
- Self-signed SSL certificates management

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
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `Policyfile.rb`: Chef Policyfile defining the run list and cookbook dependencies
- `solo.rb`: Chef Solo configuration file
- `solo.json`: Node attributes and run list for Chef Solo
- `Vagrantfile`: Vagrant configuration for local development/testing using Fedora 42
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata, with Fedora 42 used for Vagrant development environment
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
- **fail2ban Configuration**: Security hardening with fail2ban needs equivalent Ansible implementation
- **UFW Firewall Rules**: Firewall configuration must be migrated with equivalent rules
- **SSH Hardening**: SSH security settings (disabling root login, password authentication) must be preserved
- **Redis Authentication**: Redis password authentication must be maintained
- **PostgreSQL Security**: Database user creation with proper authentication

### Technical Challenges

- **Multi-site Nginx Configuration**: Ensuring the dynamic generation of site configurations is properly implemented in Ansible
- **SSL Certificate Management**: Properly handling SSL certificate generation and permissions
- **Service Dependencies**: Maintaining proper service dependencies and restart notifications
- **Idempotency**: Ensuring all operations remain idempotent, especially database user creation and certificate generation
- **Template Conversion**: Converting ERB templates to Jinja2 format for Ansible

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
   - Deploy application from Git
   - Configure systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS as specified in the cookbook metadata
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA)
3. The same security practices (fail2ban, UFW, SSH hardening) are desired in the Ansible implementation
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The Redis password "redis_secure_password_123" will need to be secured in Ansible Vault
6. The PostgreSQL credentials (fastapi/fastapi_password) will need to be secured in Ansible Vault
7. The Vagrant development environment should be preserved with equivalent functionality

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
│   ├── nginx-multisite/
│   │   ├── defaults/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   └── templates/
│   ├── cache/
│   │   ├── defaults/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   └── templates/
│   └── fastapi-tutorial/
│       ├── defaults/
│       ├── handlers/
│       ├── tasks/
│       └── templates/
├── playbooks/
│   ├── site.yml         # Main playbook
│   ├── nginx.yml        # Nginx-specific playbook
│   ├── cache.yml        # Cache services playbook
│   └── fastapi.yml      # FastAPI application playbook
├── group_vars/
│   └── all.yml          # Common variables
├── host_vars/
│   └── webserver.yml    # Host-specific variables
├── ansible.cfg          # Ansible configuration
└── Vagrantfile          # For local testing
```

## Security and Secrets Management

For the migration, we recommend:

1. Using Ansible Vault for sensitive information:
   - Redis authentication password
   - PostgreSQL credentials
   - Any API keys or tokens

2. Implementing equivalent security measures:
   - fail2ban configuration
   - UFW firewall rules
   - SSH hardening
   - SSL certificate management

## Testing Strategy

1. Develop a testing pipeline using Molecule for individual role testing
2. Use the existing Vagrant setup to test the complete playbook
3. Implement integration tests to verify:
   - Nginx site accessibility
   - SSL certificate validity
   - Redis and Memcached functionality
   - FastAPI application deployment and database connectivity

## Documentation Requirements

1. README with setup and usage instructions
2. Role-specific documentation
3. Variable documentation
4. Deployment guide
5. Testing procedures