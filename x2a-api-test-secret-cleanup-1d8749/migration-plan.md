# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-7 weeks

**Complexity Assessment**: Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations need careful migration
- Secrets management needs improvement in the Ansible implementation

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, dependency on community cookbooks

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `Vagrantfile`: Defines a Fedora 42 VM with libvirt provider for local development and testing
- `solo.json`: Chef configuration file with run list and node attributes
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules or integrate with Let's Encrypt using `geerlingguy.certbot`

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migration approach: Use Ansible's `ufw` module or consider `firewalld` for Fedora

- **SSH Hardening**:
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's `lineinfile` module or consider `dev-sec.ssh-hardening` role

- **Fail2ban Configuration**:
  - Current implementation installs and configures fail2ban
  - Migration approach: Use Ansible's `template` module or consider `geerlingguy.security` role

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe
  - PostgreSQL credentials are hardcoded in the recipe
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Preserving the dynamic generation of site configurations
  - Mitigation: Use Ansible's template module with Jinja2 templates and variable structures similar to the current node attributes

- **Redis Configuration Customization**: 
  - Challenge: The current implementation includes a hack to fix Redis configuration
  - Mitigation: Create a custom Redis template in Ansible that properly handles the configuration without requiring post-processing

- **Service Orchestration**: 
  - Challenge: Ensuring proper service restart only when needed
  - Mitigation: Use Ansible's handlers and notify mechanism, which is similar to Chef's notifications

- **Testing Environment**: 
  - Challenge: Preserving the Vagrant-based testing workflow
  - Mitigation: Update the Vagrantfile to use Ansible provisioner instead of Chef

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Dependent services that the application will need
   - Moderate complexity with external dependencies

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on the infrastructure being in place
   - Contains database setup and application configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for development, but production may require proper certificates
3. The current security configurations are appropriate for the target environment
4. The FastAPI application repository will remain available at the specified URL
5. PostgreSQL will be installed locally rather than using an external service
6. The current Redis password and PostgreSQL credentials are development values and will be replaced in production
7. The Vagrant setup is primarily for development and testing, not production deployment

## Ansible Structure Recommendation

```
ansible-infrastructure/
├── inventories/
│   ├── development/
│   │   ├── group_vars/
│   │   │   └── all.yml
│   │   └── hosts.yml
│   └── production/
│       ├── group_vars/
│       │   └── all.yml
│       └── hosts.yml
├── roles/
│   ├── nginx-multisite/
│   │   ├── defaults/
│   │   ├── files/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   ├── templates/
│   │   └── vars/
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
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
├── Vagrantfile
└── ansible.cfg
```

## Implementation Notes

1. **Variable Structure**: Preserve the hierarchical structure of Chef node attributes in Ansible variables
2. **Templates**: Convert ERB templates to Jinja2 format
3. **Idempotence**: Ensure all Ansible tasks are idempotent, similar to Chef resources
4. **Secrets**: Use Ansible Vault for sensitive information like passwords
5. **Testing**: Update the Vagrant workflow to use Ansible for consistent testing
6. **Documentation**: Create comprehensive README files for each role