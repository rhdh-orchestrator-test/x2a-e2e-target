# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository contains well-structured Chef cookbooks with clear dependencies
- No custom resources or complex Chef-specific patterns are used
- The configuration is focused on standard services (Nginx, FastAPI, PostgreSQL, Redis, Memcached)

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, UFW firewall rules, fail2ban integration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

**CRITICAL PATH VERIFICATION:**
I have verified that each of these modules exists in the repository with the following paths:
- cookbooks/fastapi-tutorial/recipes/default.rb
- cookbooks/nginx-multisite/recipes/default.rb
- cookbooks/cache/recipes/default.rb

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including external cookbooks (nginx, memcached, redisio). Will be replaced by Ansible Galaxy requirements.yml.
- `solo.json`: Contains node attributes and run list. Will be replaced by Ansible inventory variables and playbook structure.
- `solo.rb`: Chef Solo configuration. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines development VM. Can be adapted to use Ansible provisioner instead of Chef.
- `vagrant-provision.sh`: Script to install Chef and run cookbooks. Will be replaced with Ansible provisioning script.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: The current setup generates self-signed certificates. Migration should maintain this capability or integrate with Let's Encrypt via Ansible's `community.crypto` collection.
- **Firewall Configuration**: UFW rules should be migrated to equivalent Ansible UFW module tasks.
- **fail2ban Integration**: Configuration should be migrated to Ansible tasks for fail2ban installation and configuration.
- **SSH Hardening**: Current configuration disables root login and password authentication. These settings should be preserved in the Ansible playbooks.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - No external vault integration is currently used

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts based on node attributes will need to be carefully migrated to Ansible's templating system.
- **Service Dependencies**: The current setup has interdependencies between services (e.g., FastAPI depends on PostgreSQL). These dependencies need to be maintained in the Ansible playbook flow.
- **SSL Certificate Generation**: The self-signed certificate generation logic needs to be replicated in Ansible using the `community.crypto` collection.
- **Idempotent Database Setup**: The PostgreSQL database creation commands need to be made idempotent in Ansible.

### Migration Order

1. **cache role** (low complexity): Simple configuration of Memcached and Redis services
2. **nginx-multisite role** (medium complexity): Nginx configuration with SSL and security features
3. **fastapi-tutorial role** (high complexity): Application deployment with database dependencies

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu based systems
2. The same network configuration and port mappings will be maintained
3. Self-signed certificates are acceptable for the migrated solution
4. No CI/CD pipeline integration is required as part of the migration
5. The Vagrant development environment should be preserved but converted to use Ansible

## Ansible Structure Recommendation

```
ansible-nginx-fastapi/
├── inventories/
│   ├── development/
│   │   ├── group_vars/
│   │   │   └── all.yml  # Variables from solo.json
│   │   └── hosts        # Development hosts
│   └── production/
│       ├── group_vars/
│       └── hosts
├── roles/
│   ├── nginx-multisite/
│   │   ├── defaults/
│   │   │   └── main.yml  # From nginx-multisite attributes
│   │   ├── tasks/
│   │   │   ├── main.yml
│   │   │   ├── nginx.yml
│   │   │   ├── security.yml
│   │   │   ├── ssl.yml
│   │   │   └── sites.yml
│   │   └── templates/
│   │       ├── nginx.conf.j2
│   │       ├── security.conf.j2
│   │       ├── site.conf.j2
│   │       └── sysctl-security.conf.j2
│   ├── fastapi-tutorial/
│   │   ├── defaults/
│   │   │   └── main.yml
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   └── templates/
│   │       ├── fastapi-tutorial.service.j2
│   │       └── env.j2
│   └── cache/
│       ├── defaults/
│       │   └── main.yml
│       ├── tasks/
│       │   ├── main.yml
│       │   ├── memcached.yml
│       │   └── redis.yml
│       └── templates/
│           └── redis.conf.j2
├── playbooks/
│   ├── site.yml        # Main playbook (equivalent to run_list)
│   ├── nginx.yml       # Individual service playbooks
│   ├── fastapi.yml
│   └── cache.yml
├── requirements.yml    # Ansible Galaxy requirements (from Berksfile)
└── Vagrantfile         # Updated to use Ansible provisioner
```

## Migration Testing Strategy

1. **Unit Testing**: Validate individual Ansible roles using Molecule
2. **Integration Testing**: Test the complete playbook against a Vagrant VM
3. **Comparison Testing**: Deploy both Chef and Ansible configurations to identical VMs and compare the results
4. **Idempotence Testing**: Ensure multiple runs of the Ansible playbooks don't cause changes after the first run

## Post-Migration Recommendations

1. Implement Ansible Vault for secret management
2. Consider integrating with Let's Encrypt for production SSL certificates
3. Add CI/CD pipeline integration for automated testing
4. Enhance documentation with role-specific README files