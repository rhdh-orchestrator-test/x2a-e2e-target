# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with FastAPI backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks. The estimated timeline for migration is 2-3 weeks, with moderate complexity due to the security configurations and SSL certificate management.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Chef dependency manager file listing cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef configuration file with run list and node attributes
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning Chef in Vagrant VM
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW with specific rules for SSH, HTTP, and HTTPS. Migration should use Ansible's `ufw` module to maintain identical rules.
- **Fail2Ban Setup**: The cookbook configures fail2ban with custom jail settings. Use Ansible's template module to create equivalent configuration.
- **SSH Hardening**: The cookbook disables root login and password authentication based on attributes. Use Ansible's `lineinfile` module to make the same changes.
- **SSL Certificate Management**: Self-signed certificates are generated for each site. Use Ansible's `openssl_*` modules to generate equivalent certificates.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL database credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - No external vault integration is present in the current configuration

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook dynamically creates site configurations based on attributes. Ansible templates will need to replicate this dynamic behavior.
- **SSL Certificate Generation**: Self-signed certificates are generated for each site. Ansible's `openssl_certificate` module will need to be configured to match the current behavior.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL being configured first. Ansible handlers and proper task ordering will be needed.
- **Idempotency**: Some Chef resources use `not_if` guards to ensure idempotency. Equivalent Ansible conditionals will be needed.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add security hardening (fail2ban, ufw, sysctl)
   - Implement SSL certificate generation
   - Configure virtual hosts

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on database)
   - Set up PostgreSQL database and user
   - Deploy application from Git
   - Configure Python environment and dependencies
   - Create systemd service

### Assumptions

1. The target environment will continue to be either Ubuntu (>= 18.04) or CentOS (>= 7.0)
2. The Vagrant development environment will be maintained with Fedora 42
3. Self-signed certificates are acceptable for the migrated solution
4. The current hardcoded credentials will be maintained in the initial migration
5. The directory structure for web content and SSL certificates will remain the same
6. The FastAPI application source repository will remain available at the specified URL
7. The current security settings (fail2ban, ufw, sysctl) are appropriate for the target environment

## Implementation Details

### Ansible Structure

The proposed Ansible structure will be:

```
ansible/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml
├── roles/
│   ├── nginx-multisite/
│   ├── cache/
│   └── fastapi-tutorial/
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
└── vagrant-provision.sh
```

### Secrets Management

For the initial migration, secrets will be stored in group_vars, but a recommendation for future improvement is to implement Ansible Vault for securing:

1. Redis authentication password
2. PostgreSQL database credentials
3. Any other sensitive information

### Testing Strategy

1. Develop and test each role independently
2. Use Vagrant for local testing with the same VM configuration
3. Verify functionality matches the original Chef implementation
4. Test idempotency by running playbooks multiple times

### Documentation

Each Ansible role should include:
1. README.md with usage instructions
2. Variable documentation
3. Example playbooks
4. Dependencies and requirements