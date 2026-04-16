# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity:** Medium to High
- Multiple interconnected services
- Security configurations
- SSL certificate management
- Database setup and configuration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible Galaxy requirements.yml
- `Policyfile.rb`: Chef policy definition - will be replaced by Ansible playbook structure
- `solo.json`: Chef node configuration - will be converted to Ansible inventory variables
- `solo.rb`: Chef configuration - no direct Ansible equivalent needed
- `Vagrantfile`: VM configuration for development - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible playbook

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management modules (openssl_*)

### Security Considerations

- **Firewall (ufw)**: Migrate to Ansible's `firewalld` or `ufw` modules
- **fail2ban**: Configure using Ansible's template module for configuration files
- **SSL Certificates**: Use Ansible's `openssl_*` modules for certificate generation
- **SSH Hardening**: Use Ansible's `lineinfile` or templates to configure SSH security
- **Redis Authentication**: Ensure password is stored securely in Ansible Vault
- **PostgreSQL Credentials**: Store database credentials in Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: Create a flexible Ansible role that can handle multiple site configurations from variables
- **SSL Certificate Management**: Implement proper certificate generation and renewal processes
- **Service Dependencies**: Ensure proper ordering of service deployment (database before application, etc.)
- **Idempotency**: Ensure all operations are idempotent, especially database user/schema creation

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Basic Nginx installation
   - Security configurations (fail2ban, firewall)
   - SSL certificate generation
   - Virtual host configuration

2. **cache** (low complexity, independent service)
   - Memcached configuration
   - Redis installation and security

3. **fastapi-tutorial** (high complexity, depends on database)
   - PostgreSQL installation and configuration
   - Application deployment
   - Service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or other CA)
3. The same security measures (fail2ban, firewall, SSH hardening) will be maintained
4. The FastAPI application repository will remain available at the specified URL
5. Redis and Memcached configurations will remain similar
6. The multi-site configuration pattern will be preserved

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
│   │   └── templates/
│   ├── cache/
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
├── requirements.yml
└── Vagrantfile
```

## Testing Strategy

1. Create a Vagrant environment similar to the current one but using Ansible provisioning
2. Implement incremental testing of each role
3. Verify functionality matches the current Chef implementation
4. Test idempotency (running Ansible multiple times should not change the result)
5. Validate security configurations

## Documentation Requirements

1. README with setup instructions
2. Role documentation with all available variables
3. Example inventory configurations
4. Deployment guides for development and production environments