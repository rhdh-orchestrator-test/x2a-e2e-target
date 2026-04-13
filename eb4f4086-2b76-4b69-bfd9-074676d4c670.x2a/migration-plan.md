# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks, their dependencies, and security configurations to equivalent Ansible roles and playbooks.

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
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

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

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `Policyfile.rb`: Defines the Chef policy with run list and cookbook dependencies
- `solo.json`: Contains node attributes including Nginx site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines a Fedora 42 VM for development/testing with port forwarding and resource allocation
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports Ubuntu 18.04+ and CentOS 7.0+ (based on cookbook metadata), with development environment using Fedora 42 (from Vagrantfile)
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management tasks or community.crypto collection

### Security Considerations

- **fail2ban configuration**: Migrate fail2ban configuration to Ansible tasks or dedicated role
- **UFW firewall rules**: Use Ansible's ufw module to configure firewall rules
- **SSH hardening**: Implement SSH security configurations using Ansible's lineinfile or template modules
- **Redis authentication**: Ensure Redis password is stored securely in Ansible Vault
- **PostgreSQL credentials**: Store database credentials in Ansible Vault
- **SSL certificates**: Implement proper certificate management with Ansible's crypto modules

### Technical Challenges

- **Multi-site Nginx configuration**: Ensure the Ansible role can handle multiple virtual hosts with different SSL certificates
- **Service dependencies**: Maintain proper ordering of service installation and configuration
- **Idempotency**: Ensure all operations (especially database creation) are idempotent
- **SSL certificate generation**: Implement self-signed certificate generation for development environments
- **System tuning**: Migrate sysctl security configurations properly

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation
   - Implement security configurations
   - Add SSL certificate management
   - Configure virtual hosts

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on database)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service
   - Integrate with Nginx virtual hosts

### Assumptions

1. The target environment will continue to be Linux-based (Ubuntu/CentOS/Fedora)
2. Self-signed certificates are acceptable for development environments
3. The same security hardening approach will be maintained
4. The FastAPI application source code will remain available at the same Git repository
5. Redis and PostgreSQL passwords in the Chef recipes are placeholders and will be replaced with secure values
6. The Nginx sites configuration in solo.json represents the production configuration
7. No custom Chef resources are used that would require special handling in Ansible
8. The current VM specifications (2GB RAM, 2 CPUs) are sufficient for the application stack

## Ansible Structure Recommendation

```
ansible-nginx-multisite/
├── inventories/
│   ├── development/
│   │   └── hosts.yml
│   └── production/
│       └── hosts.yml
├── group_vars/
│   ├── all/
│   │   ├── main.yml
│   │   └── vault.yml  # For secrets
│   └── webservers/
│       └── main.yml
├── roles/
│   ├── nginx_multisite/
│   │   ├── defaults/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   └── templates/
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
├── requirements.yml  # For Ansible Galaxy dependencies
└── vagrant.yml      # For local development
```

## Testing Strategy

1. Develop Vagrant configuration for Ansible to match the current Chef setup
2. Implement molecule tests for each role
3. Create integration tests to verify the complete stack works together
4. Test SSL certificate generation and virtual host configurations
5. Verify security configurations with appropriate scanning tools

## Knowledge Transfer Plan

1. Document each Ansible role with README files explaining usage and variables
2. Create example playbooks showing how to use the roles in different scenarios
3. Provide a migration guide for Chef users transitioning to the Ansible codebase
4. Document any changes in behavior or configuration between Chef and Ansible implementations