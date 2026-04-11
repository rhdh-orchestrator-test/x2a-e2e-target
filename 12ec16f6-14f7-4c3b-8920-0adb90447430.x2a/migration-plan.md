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
- The repository has well-structured Chef cookbooks with clear dependencies
- Security configurations are present and need careful migration
- External cookbook dependencies need to be replaced with Ansible Galaxy roles or custom implementations

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
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `Policyfile.rb`: Chef policy file defining the run list and cookbook dependencies
- `Vagrantfile`: Defines the development VM configuration using Vagrant
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `solo.json`: Configuration data for Chef Solo, contains site configurations and security settings
- `solo.rb`: Chef Solo configuration file

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata files. The Vagrantfile uses Fedora 42 as the development environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider as indicated in the Vagrantfile
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible Galaxy `geerlingguy.memcached` role or custom implementation
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy `geerlingguy.redis` role or custom implementation
- **ssl_certificate (~> 2.1)**: Replace with Ansible's `openssl_*` modules for certificate management

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migrate to Ansible's `openssl_certificate` module or consider integrating with Let's Encrypt using `geerlingguy.certbot`.
- **Firewall Configuration**: UFW configuration needs to be migrated to Ansible's `ufw` module or `firewalld` module depending on target OS.
- **fail2ban**: Migrate fail2ban configuration to Ansible Galaxy `geerlingguy.security` role or custom implementation.
- **SSH Hardening**: Current implementation disables root login and password authentication. Migrate to Ansible's `sshd` module or `geerlingguy.security` role.
- **Redis Authentication**: Redis is configured with password authentication. Ensure secure password handling in Ansible using Ansible Vault.

### Technical Challenges

- **Multi-site Nginx Configuration**: The current implementation uses Chef templates to generate site configurations. Ansible templates will need to be created with similar functionality.
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be migrated to Ansible's `openssl_*` modules.
- **System Hardening**: Security configurations in `security.rb` need careful migration to ensure all hardening measures are preserved.
- **PostgreSQL Database Setup**: Database and user creation for FastAPI application needs to be migrated to Ansible's `postgresql_*` modules.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add site configuration templates
   - Add security hardening features

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Implement PostgreSQL database setup
   - Implement Python environment and application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS as specified in the cookbook metadata.
2. Self-signed certificates are acceptable for the migrated solution, or an alternative certificate management solution will be specified.
3. The Redis password in the Chef cookbook (`redis_secure_password_123`) is a placeholder and will be replaced with a secure password stored in Ansible Vault.
4. The PostgreSQL credentials in the FastAPI application setup are also placeholders to be secured with Ansible Vault.
5. The FastAPI application source will continue to be available at the specified GitHub repository.
6. The Vagrant development environment will be maintained for testing the Ansible playbooks.

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
├── group_vars/
│   └── all/
│       ├── vars.yml
│       └── vault.yml
└── vagrant/
    └── Vagrantfile
```

## Next Steps

1. Create a basic Ansible project structure following the recommendation above
2. Set up Ansible Vault for secure storage of credentials
3. Begin developing the `nginx-multisite` role
4. Set up a CI/CD pipeline for testing Ansible playbooks
5. Develop and test each role in sequence according to the migration order
6. Create comprehensive documentation for the new Ansible infrastructure
7. Conduct knowledge transfer sessions with the team