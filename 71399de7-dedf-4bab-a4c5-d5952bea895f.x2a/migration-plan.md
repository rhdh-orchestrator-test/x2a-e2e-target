# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three primary cookbooks with their dependencies, security configurations, and service orchestration.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Multiple interconnected services
- Security hardening requirements
- SSL certificate management
- Database integration

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

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio, etc.)
- `Policyfile.rb`: Chef policy file defining the run list and cookbook versions
- `solo.json`: Configuration data for Chef Solo with site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines the development VM (Fedora 42) with networking and provisioning
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used for development
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., geerlingguy.redis)
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management (ansible.posix.openssl_* modules)

### Security Considerations

- **Firewall (ufw)**: Migrate to Ansible firewall module (ansible.posix.ufw)
- **Fail2ban**: Create Ansible role for fail2ban configuration
- **SSH hardening**: Implement using ansible.posix.ssh_config module
- **SSL certificates**: Generate self-signed certificates using openssl_* modules
- **Redis authentication**: Ensure password is stored securely in Ansible Vault
- **PostgreSQL credentials**: Store database credentials in Ansible Vault

### Technical Challenges

- **Multi-site configuration**: Ensure the Ansible role can handle multiple Nginx sites with proper templating
- **SSL certificate management**: Implement proper certificate generation and renewal process
- **Service dependencies**: Maintain proper ordering of service deployment (database before application, etc.)
- **Configuration templating**: Convert Chef templates to Ansible templates with proper variable substitution
- **Idempotency**: Ensure all operations are idempotent, especially database user/schema creation

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Basic Nginx installation
   - Security hardening (fail2ban, firewall)
   - SSL certificate generation
   - Virtual host configuration

2. **cache** (low complexity, independent service)
   - Memcached configuration
   - Redis installation and security

3. **fastapi-tutorial** (high complexity, depends on database)
   - PostgreSQL installation and configuration
   - Python environment setup
   - Application deployment
   - Service configuration

### Assumptions

1. The target environment will continue to be Linux-based (Ubuntu/CentOS/Fedora)
2. Self-signed certificates are acceptable for development (production would require proper CA)
3. The same security hardening requirements will apply in the new environment
4. The FastAPI application repository will remain available at the same URL
5. The current VM specifications (2GB RAM, 2 CPUs) are sufficient for the application stack
6. Network ports and configurations will remain the same
7. No additional monitoring or logging requirements beyond what's in the current Chef setup

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
│   ├── nginx_multisite/
│   ├── cache_services/
│   └── fastapi_app/
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
├── templates/
├── files/
└── ansible.cfg
```

## Testing Strategy

1. Develop using Vagrant with Ansible provisioner instead of Chef
2. Create molecule tests for each role
3. Implement integration testing with a full stack deployment
4. Verify all sites are accessible and properly configured
5. Validate security configurations match the original Chef implementation

## Knowledge Transfer Plan

1. Document each Ansible role with README files
2. Create a deployment guide for the full stack
3. Provide comparison documentation between Chef and Ansible implementations
4. Schedule knowledge transfer sessions with the team