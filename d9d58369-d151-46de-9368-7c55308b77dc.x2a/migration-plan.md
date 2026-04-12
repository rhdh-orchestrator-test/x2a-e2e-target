# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-7 weeks

**Complexity Assessment**: Medium
- The codebase is well-structured with clear separation of concerns
- Security configurations are explicit and can be directly mapped to Ansible
- External dependencies on community cookbooks will need equivalent Ansible Galaxy roles

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git-based deployment, PostgreSQL database provisioning, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio, ssl_certificate)
- `Policyfile.rb`: Chef Policyfile defining the run list and cookbook dependencies
- `solo.json`: Configuration data for Chef Solo with site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Vagrant configuration for local development using Fedora 42
- `vagrant-provision.sh`: Provisioning script for Vagrant to install Chef and run cookbooks

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible Galaxy `geerlingguy.memcached` role
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy `geerlingguy.redis` role
- **ssl_certificate (~> 2.1)**: Replace with Ansible's `openssl_*` modules for certificate generation

### Security Considerations

- **Firewall (UFW)**: Migrate UFW rules to Ansible's `ufw` module
- **Fail2ban**: Use Ansible to install and configure fail2ban with appropriate jail settings
- **SSH Hardening**: Maintain SSH security settings using Ansible's `lineinfile` or templates
- **SSL Certificates**: Ensure proper handling of self-signed certificates and private keys
- **Redis Authentication**: Maintain Redis password authentication in Ansible configuration
- **PostgreSQL Security**: Properly handle database credentials and access control
- **Sysctl Security Settings**: Migrate kernel parameter security settings

### Technical Challenges

- **Multi-site Nginx Configuration**: Ensure the dynamic generation of site configurations is properly implemented in Ansible
- **SSL Certificate Management**: Handle certificate generation and renewal process
- **Service Dependencies**: Maintain proper ordering of service installations and configurations
- **Idempotency**: Ensure all operations are idempotent, especially database user creation and schema setup
- **Environment Variables**: Properly handle environment configuration for the FastAPI application

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Implement security hardening (fail2ban, ufw)
   - Add SSL certificate generation
   - Configure virtual hosts

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on database)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions
2. Self-signed certificates are acceptable for development/testing environments
3. The same security requirements will be maintained in the Ansible implementation
4. The FastAPI application source code will continue to be pulled from the same Git repository
5. Redis and Memcached configurations will maintain the same performance characteristics
6. No changes to the application architecture are required during migration
7. The Vagrant development environment will be maintained but converted to use Ansible provisioner
8. No CI/CD pipeline integration is required as part of the migration