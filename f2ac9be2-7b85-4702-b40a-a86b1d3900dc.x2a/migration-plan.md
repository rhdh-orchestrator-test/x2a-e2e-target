# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3-4 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7-8 weeks

**Complexity Assessment:** Medium
- Multiple interconnected services
- Security configurations
- SSL certificate management
- Database integration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible Galaxy requirements.yml
- `Policyfile.rb`: Chef policy definition - will be replaced by Ansible playbook structure
- `solo.json`: Chef node configuration - will be converted to Ansible inventory variables
- `solo.rb`: Chef configuration - no direct Ansible equivalent needed
- `Vagrantfile`: VM configuration for development - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible playbook

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>=18.04) and CentOS (>=7.0), with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management modules (openssl_*)

### Security Considerations

- **Firewall (ufw)**: Migrate to Ansible's `ufw` module for firewall management
- **fail2ban**: Use Ansible to configure fail2ban with appropriate jails
- **SSH hardening**: Migrate SSH security configurations using Ansible's `lineinfile` or templates
- **SSL certificates**: Use Ansible's `openssl_*` modules for certificate generation
- **Redis authentication**: Ensure Redis password is stored securely in Ansible Vault
- **PostgreSQL credentials**: Store database credentials in Ansible Vault

### Technical Challenges

- **Multi-site configuration**: Ensure the Ansible role can handle multiple Nginx sites with proper templating
- **SSL certificate management**: Implement proper certificate generation and renewal processes
- **Service dependencies**: Maintain proper ordering of service installation and configuration
- **Idempotency**: Ensure all operations are idempotent, especially database user/schema creation
- **Configuration compatibility**: Ensure Ansible-generated configurations match Chef-generated ones for seamless migration

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create base Nginx role
   - Implement multi-site configuration
   - Implement SSL certificate management
   - Implement security hardening

2. **cache** (low complexity, standalone services)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on database)
   - Implement PostgreSQL installation and configuration
   - Implement Python application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be either Ubuntu (>=18.04) or CentOS (>=7.0)
2. The same security requirements will apply in the new environment
3. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or similar)
4. The FastAPI application repository will remain available at the specified URL
5. The Redis password and PostgreSQL credentials in the Chef recipes are development values and will be replaced with secure values in production
6. The Nginx sites configuration (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same
7. The current Chef setup is functional and represents the desired end state for Ansible

## Implementation Details

### Ansible Structure

```
ansible/
├── inventory/
│   ├── group_vars/
│   │   ├── all.yml
│   │   └── webservers.yml
│   └── hosts
├── roles/
│   ├── nginx-multisite/
│   ├── cache/
│   └── fastapi-tutorial/
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
└── requirements.yml
```

### Key Ansible Modules to Use

- **nginx-multisite**:
  - `package`: Install Nginx and security packages
  - `template`: Configure Nginx configuration files
  - `file`: Manage directories and symbolic links
  - `openssl_*`: Generate SSL certificates
  - `ufw`: Configure firewall rules
  - `service`: Manage Nginx service

- **cache**:
  - `package`: Install Redis and Memcached
  - `template`: Configure Redis and Memcached
  - `service`: Manage Redis and Memcached services

- **fastapi-tutorial**:
  - `package`: Install Python and PostgreSQL packages
  - `git`: Clone application repository
  - `command`: Create Python virtual environment
  - `pip`: Install Python dependencies
  - `postgresql_*`: Configure PostgreSQL database and users
  - `template`: Create application configuration files
  - `systemd`: Configure application service

### Testing Strategy

1. Develop Vagrant-based test environment similar to the current setup
2. Create molecule tests for individual roles
3. Implement integration tests to verify multi-service functionality
4. Compare outputs and configurations between Chef and Ansible implementations