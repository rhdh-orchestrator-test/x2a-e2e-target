# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three primary Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3-4 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7-8 weeks

**Complexity Assessment:** Medium to High
- Multiple interconnected services
- Security configurations that need careful migration
- Database and application deployment with specific configurations

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
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

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `Policyfile.rb`: Defines the Chef policy with run list and cookbook dependencies
- `solo.json`: Configuration data for Chef solo, contains site configurations and security settings
- `solo.rb`: Chef solo configuration file defining paths and log settings
- `Vagrantfile`: Defines the development VM using Fedora 42, with port forwarding and network configuration
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora (based on Vagrantfile specifying "generic/fedora42"), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (specified in Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., geerlingguy.redis)
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management tasks or community.crypto collection

### Security Considerations

- **Firewall (UFW)**: Migrate UFW rules to Ansible firewall module
- **Fail2ban**: Configure fail2ban using Ansible to match current settings
- **SSH Hardening**: Ensure SSH security settings (disable root login, password authentication) are maintained
- **SSL Certificates**: Properly handle self-signed certificate generation and permissions
- **Redis Authentication**: Securely manage Redis password (currently hardcoded as 'redis_secure_password_123')
- **PostgreSQL Authentication**: Securely manage database credentials (currently hardcoded as 'fastapi_password')

### Technical Challenges

- **Multi-site Nginx Configuration**: Ensure the dynamic generation of multiple virtual hosts is properly implemented in Ansible
- **SSL Certificate Management**: Properly handle certificate generation and permissions
- **Service Orchestration**: Ensure proper service start order and dependencies
- **Environment Configuration**: Manage environment variables and configuration files for the FastAPI application
- **Idempotency**: Ensure database creation tasks are idempotent (current implementation uses "|| true" to handle errors)

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Base Nginx configuration
   - SSL certificate management
   - Virtual host configuration
   - Security hardening (fail2ban, ufw)

2. **cache** (low complexity, standalone services)
   - Memcached configuration
   - Redis installation and configuration

3. **fastapi-tutorial** (high complexity, depends on database)
   - PostgreSQL installation and configuration
   - Python environment setup
   - Application deployment
   - Service configuration

### Assumptions

1. The target environment will continue to be Fedora-based, with support for Ubuntu and CentOS
2. The current network configuration and port mappings will be maintained
3. Self-signed certificates are acceptable for development/testing
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment
6. The hardcoded credentials in the Chef recipes will be replaced with Ansible Vault or another secure credential management solution

## Ansible Structure Recommendation

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
├── files/
│   └── ssl/
└── templates/
    ├── nginx/
    └── systemd/
```

## Implementation Notes

1. **Secrets Management**: Use Ansible Vault to secure sensitive information like database passwords and Redis authentication
2. **Templates**: Convert Chef templates to Ansible Jinja2 templates
3. **Handlers**: Replace Chef notifications with Ansible handlers
4. **Variables**: Move Chef attributes to Ansible variables in group_vars or role defaults
5. **Idempotency**: Ensure all tasks are idempotent, especially database creation and user management
6. **Testing**: Implement molecule tests for each role to ensure proper functionality

## Validation Strategy

1. Deploy to a test environment using the same VM configuration as specified in the Vagrantfile
2. Verify all sites are accessible via HTTP/HTTPS
3. Validate security configurations (firewall rules, fail2ban, SSH settings)
4. Test Redis authentication and functionality
5. Verify FastAPI application deployment and database connectivity
6. Perform load testing to ensure performance is comparable to the Chef implementation