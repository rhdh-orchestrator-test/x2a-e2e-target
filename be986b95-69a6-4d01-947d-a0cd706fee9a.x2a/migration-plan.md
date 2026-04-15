# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx configuration with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three primary cookbooks with their dependencies to equivalent Ansible roles and playbooks.

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
- Self-signed SSL certificates that need to be managed

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
- `Policyfile.rb`: Chef policy file defining the run list and cookbook dependencies
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `solo.json`: Node attributes and run list for Chef Solo
- `Vagrantfile`: Defines a Fedora 42 VM for development and testing
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata, with Fedora 42 used for development in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider as indicated in the Vagrantfile
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `ansible.posix.nginx`)
- **ssl_certificate (~> 2.1)**: Replace with Ansible's `community.crypto` collection for certificate management
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: Self-signed certificates are generated for development; maintain this capability while providing a path for production certificates
- **Firewall Configuration**: UFW configuration needs to be migrated to equivalent Ansible firewall modules
- **fail2ban Setup**: Ensure fail2ban configuration is properly migrated
- **SSH Hardening**: Maintain SSH security settings (disable root login, password authentication)
- **Redis Authentication**: Ensure Redis password is securely managed in Ansible Vault
- **PostgreSQL Authentication**: Database credentials need to be securely stored in Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: Ensure the dynamic generation of site configurations is properly implemented in Ansible
- **SSL Certificate Generation**: Implement equivalent self-signed certificate generation logic
- **Service Dependencies**: Maintain proper ordering of service installations and configurations
- **Python Environment Management**: Ensure proper setup of Python virtual environments
- **Database Initialization**: Ensure PostgreSQL database creation and user setup is idempotent

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation
   - Add SSL certificate management
   - Implement site configuration templates
   - Add security hardening features

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on database)
   - Set up PostgreSQL database
   - Configure Python environment
   - Deploy application from Git
   - Set up systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based distributions
2. Self-signed certificates are acceptable for development, but production deployment may require integration with Let's Encrypt or other certificate providers
3. The security hardening measures (fail2ban, UFW, SSH configuration) are required in the migrated solution
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. Redis authentication is required in the migrated solution
6. The current directory structure and naming conventions can be adapted to Ansible best practices

## Ansible Structure Recommendation

```
ansible-nginx-multisite/
├── inventories/
│   ├── development/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   │       ├── all.yml
│   │       └── web_servers.yml
│   └── production/
│       ├── hosts.yml
│       └── group_vars/
│           ├── all.yml
│           └── web_servers.yml
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
├── vagrant/
│   └── Vagrantfile
└── ansible.cfg
```

## Implementation Notes

1. **Variable Management**:
   - Move Chef attributes to Ansible variables in `defaults/main.yml` or inventory group_vars
   - Use Ansible Vault for sensitive information (Redis password, PostgreSQL credentials)

2. **Template Conversion**:
   - Convert ERB templates to Jinja2 format
   - Maintain the same configuration structure where possible

3. **Idempotence**:
   - Ensure all tasks are idempotent, especially database creation and user setup
   - Use Ansible's state management features instead of Chef's not_if/only_if guards

4. **Testing Strategy**:
   - Maintain Vagrant for development testing
   - Consider adding Molecule for role testing
   - Implement integration tests to verify complete functionality

5. **Documentation**:
   - Document each role with README.md files
   - Include example playbooks and variable configurations
   - Document security considerations and vault usage