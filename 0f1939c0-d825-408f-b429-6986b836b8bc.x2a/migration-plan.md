# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three primary Chef cookbooks to Ansible roles and playbooks, addressing external dependencies, and ensuring security configurations are properly maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Moderate number of external dependencies (nginx, memcached, redis)
- Security configurations that need careful migration
- Database integration requiring proper credential management

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
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `solo.json`: Node attributes and run list configuration for Chef Solo
- `Vagrantfile`: Defines a Fedora 42 VM for development/testing with port forwarding and networking
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

Based on the source repository analysis:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata files. The Vagrantfile uses Fedora 42.
- **Virtual Machine Technology**: Vagrant with libvirt provider as indicated in the Vagrantfile
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or use the `ansible.builtin.package` module with templates
- **memcached (~> 6.0)**: Use Ansible's `memcached` role or the `ansible.builtin.package` module with appropriate configuration
- **redisio (~> 7.2.4)**: Use Ansible Galaxy's `redis` role or create a custom role for Redis installation and configuration
- **ssl_certificate (~> 2.1)**: Use Ansible's `openssl_*` modules for certificate management

### Security Considerations

- **SSL Certificate Management**: Migrate self-signed certificate generation to Ansible's `openssl_certificate` module
- **fail2ban Configuration**: Create an Ansible role to install and configure fail2ban with similar jail settings
- **UFW Firewall Rules**: Use Ansible's `ufw` module to replicate the firewall configuration
- **SSH Hardening**: Ensure SSH security settings are applied using Ansible's `lineinfile` or templates
- **Redis Password**: Store Redis authentication password in Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of site configurations based on node attributes will need careful translation to Ansible variables and templates
- **SSL Certificate Management**: Ensuring proper permissions and ownership of SSL certificates and keys
- **Service Dependencies**: Maintaining the correct order of service installation and configuration, especially for the FastAPI application that depends on PostgreSQL
- **Idempotency**: Ensuring all database creation and user setup operations are idempotent

### Migration Order

1. **cache role** (low complexity): Simple installation and configuration of Memcached and Redis
2. **nginx-multisite role** (medium complexity): Nginx installation, configuration, and SSL setup
3. **fastapi-tutorial role** (high complexity): Application deployment with database dependencies

### Assumptions

1. The target environment will continue to support either Ubuntu (>= 18.04) or CentOS (>= 7.0)
2. The self-signed certificates approach is acceptable for the migrated solution (not using Let's Encrypt or other CA)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" will be migrated to Ansible Vault
5. The Vagrant development environment will be maintained but converted to use Ansible provisioner instead of Chef

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
│   │   │   └── main.yml  # Default variables (sites configuration)
│   │   ├── tasks/
│   │   │   ├── main.yml
│   │   │   ├── nginx.yml
│   │   │   ├── security.yml
│   │   │   ├── sites.yml
│   │   │   └── ssl.yml
│   │   └── templates/
│   │       ├── nginx.conf.j2
│   │       ├── security.conf.j2
│   │       └── site.conf.j2
│   ├── cache/
│   │   ├── defaults/
│   │   │   └── main.yml  # Redis and Memcached configuration
│   │   ├── tasks/
│   │   │   ├── main.yml
│   │   │   ├── memcached.yml
│   │   │   └── redis.yml
│   │   └── templates/
│   │       └── redis.conf.j2
│   └── fastapi-tutorial/
│       ├── defaults/
│       │   └── main.yml  # Application configuration
│       ├── tasks/
│       │   ├── main.yml
│       │   ├── app.yml
│       │   └── database.yml
│       └── templates/
│           ├── env.j2
│           └── fastapi-tutorial.service.j2
├── playbooks/
│   ├── site.yml         # Main playbook
│   ├── nginx.yml        # Nginx-specific playbook
│   ├── cache.yml        # Cache services playbook
│   └── fastapi.yml      # FastAPI application playbook
├── Vagrantfile          # Updated for Ansible provisioning
└── ansible.cfg          # Ansible configuration
```

## Security Migration Notes

1. **SSL Certificates**: Replace Chef's `openssl` command execution with Ansible's `openssl_certificate` module
2. **Firewall Rules**: Use Ansible's `ufw` module instead of Chef's `execute` resources
3. **SSH Hardening**: Use Ansible's `lineinfile` or templates to configure SSH security settings
4. **Secrets Management**: Store sensitive information (Redis password, PostgreSQL credentials) in Ansible Vault
5. **fail2ban**: Create templates for fail2ban configuration similar to Chef's approach

## Testing Strategy

1. Develop and test each role individually using Molecule
2. Create integration tests to verify interactions between roles
3. Use the existing Vagrant setup with Ansible provisioner for full-stack testing
4. Verify all security configurations are correctly applied
5. Test idempotency of all playbooks

## Knowledge Transfer Plan

1. Document each Ansible role with README files explaining purpose and configuration options
2. Create example playbooks showing how to use the roles
3. Provide variable reference documentation
4. Conduct knowledge sharing sessions with the team
5. Create a comparison guide between the original Chef implementation and new Ansible structure