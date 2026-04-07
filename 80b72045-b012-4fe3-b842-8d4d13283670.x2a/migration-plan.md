# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Multiple interconnected services
- Security configurations that need careful migration
- External dependencies on community cookbooks that need Ansible equivalents

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible Galaxy requirements.yml
- `Policyfile.rb`: Chef policy definition - will be replaced by Ansible playbook structure
- `solo.json`: Chef node configuration - will be converted to Ansible inventory variables
- `solo.rb`: Chef configuration file - will be replaced by ansible.cfg
- `Vagrantfile`: VM configuration for development - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible playbook

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management tasks or community.crypto collection

### Security Considerations

- **SSL Certificate Management**: Currently using self-signed certificates; migration should maintain or improve security by using Ansible's crypto modules
- **Firewall Configuration**: UFW firewall rules need to be migrated to Ansible UFW module
- **fail2ban Configuration**: Fail2ban setup needs to be migrated to Ansible tasks
- **SSH Hardening**: SSH security configurations (disable root login, password authentication) need to be preserved
- **Redis Authentication**: Redis password needs to be securely managed in Ansible Vault
- **PostgreSQL Credentials**: Database credentials need to be securely managed in Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts with SSL needs careful implementation in Ansible
- **Service Orchestration**: The interdependencies between services (PostgreSQL before FastAPI, etc.) need to be maintained
- **Template Conversion**: Chef templates need to be converted to Jinja2 format for Ansible
- **Idempotency**: Ensuring all operations remain idempotent, especially database creation and user setup
- **Configuration Flexibility**: Maintaining the same level of configuration flexibility in Ansible variables

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Base Nginx installation
   - Security hardening (fail2ban, ufw)
   - SSL certificate generation
   - Virtual host configuration

2. **cache** (low complexity, independent service)
   - Memcached configuration
   - Redis installation and security

3. **fastapi-tutorial** (high complexity, depends on other services)
   - PostgreSQL database setup
   - Python environment configuration
   - Application deployment
   - Service configuration

### Assumptions

1. The target environment will continue to be Linux-based (Ubuntu/CentOS/Fedora)
2. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or other CA)
3. The same security policies should be maintained in the Ansible implementation
4. The FastAPI application source will continue to be pulled from the same Git repository
5. The multi-site configuration pattern will be maintained with the same domain structure
6. Redis and Memcached will continue to be used as caching solutions
7. The current directory structure in the target environment (/var/www/, /opt/fastapi-tutorial) will be maintained

## Ansible Structure Recommendation

```
ansible-nginx-multisite/
├── ansible.cfg
├── inventory/
│   ├── group_vars/
│   │   ├── all.yml
│   │   └── webservers.yml
│   └── hosts.ini
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
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
└── requirements.yml
```

## Testing Strategy

1. Develop a Vagrant-based testing environment similar to the current setup
2. Create molecule tests for each role
3. Implement integration tests to verify the complete stack works together
4. Compare outputs and configurations with the original Chef implementation to ensure parity

## Documentation Requirements

1. README with setup instructions
2. Role-specific documentation
3. Variable reference guide
4. Security considerations and best practices
5. Testing procedures