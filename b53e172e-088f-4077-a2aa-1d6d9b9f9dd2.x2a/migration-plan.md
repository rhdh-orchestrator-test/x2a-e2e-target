# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations need careful migration
- Redis configuration has custom hacks that will need special attention

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, custom Redis configuration fixes

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, ssl_certificate, memcached, redisio)
- `Policyfile.rb`: Chef Policyfile defining the run list and cookbook dependencies
- `solo.json`: Node configuration with site details, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Provisioning script for Vagrant VM setup
- `Vagrantfile`: Vagrant configuration for development environment

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create custom Nginx role
- **ssl_certificate (~> 2.1)**: Replace with Ansible's `openssl_*` modules for certificate management
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **fail2ban configuration**: Migrate using Ansible's package and template modules to configure fail2ban
- **ufw firewall rules**: Use Ansible's `ufw` module to configure firewall rules
- **SSH hardening**: Use Ansible's `lineinfile` module to configure SSH security settings
- **Redis authentication**: Ensure Redis password is stored securely in Ansible Vault
- **PostgreSQL credentials**: Store database credentials in Ansible Vault
- **SSL certificates**: Use Ansible's `openssl_*` modules for certificate generation and management

### Technical Challenges

- **Redis configuration hack**: The Chef cookbook includes a Ruby block to modify Redis configuration files after they're created. This will need a custom approach in Ansible, possibly using the `lineinfile` module or a custom template.
- **Multi-site Nginx configuration**: The dynamic generation of Nginx site configurations will need to be replicated using Ansible's templating system.
- **SSL certificate generation**: Self-signed certificate generation will need to be implemented using Ansible's `openssl_*` modules.
- **PostgreSQL user and database creation**: Will need to use Ansible's PostgreSQL modules which may have different syntax than the Chef commands.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create base Nginx role
   - Implement SSL certificate generation
   - Configure virtual hosts
   - Implement security hardening

2. **cache** (moderate complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Address Redis configuration hack

3. **fastapi-tutorial** (high complexity, depends on database)
   - Implement PostgreSQL installation and configuration
   - Configure Python environment and dependencies
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu based systems
2. Self-signed certificates are acceptable for development environments
3. The same security hardening measures will be maintained
4. The FastAPI application repository will remain available at the same URL
5. The Redis configuration hack is still necessary in the current version of Redis
6. The Vagrant development environment will be maintained but converted to use Ansible provisioner

## Ansible Structure Recommendation

```
ansible-nginx-multisite/
├── inventories/
│   ├── development/
│   │   ├── group_vars/
│   │   │   ├── all/
│   │   │   │   ├── vars.yml
│   │   │   │   └── vault.yml
│   │   │   └── web/
│   │   │       └── vars.yml
│   │   └── hosts.yml
│   └── production/
│       └── ...
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
│   └── fastapi_tutorial/
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

1. Create Ansible roles for each cookbook
2. Update Vagrantfile to use Ansible provisioner
3. Test each role individually
4. Test complete playbook against Vagrant VM
5. Verify all sites and services are functioning correctly
6. Validate security configurations

## Documentation Requirements

1. README with setup instructions
2. Role documentation with variables and examples
3. Inventory structure documentation
4. Vault usage guidelines for secrets management
5. Testing procedures