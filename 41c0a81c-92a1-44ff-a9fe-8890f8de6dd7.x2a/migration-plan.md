# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx configuration with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Core Infrastructure Migration: 2 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5 weeks

**Complexity Assessment**: Medium
- Multiple interconnected services
- Security configurations that need careful migration
- External dependencies on community cookbooks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), sysctl security settings

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

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `Policyfile.rb`: Defines the run list and cookbook dependencies for Chef Policyfile workflow
- `solo.json`: Contains node attributes including Nginx site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration (Fedora 42) with port forwarding and networking

### Target Details

Based on the source repository analysis:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible `geerlingguy.memcached` role
- **redisio (~> 7.2.4)**: Replace with Ansible `geerlingguy.redis` or DavidWittman.redis role
- **ssl_certificate (~> 2.1)**: Replace with Ansible `community.crypto` collection for certificate management

### Security Considerations

- **fail2ban configuration**: Migrate fail2ban jail configuration to Ansible using templates
- **ufw firewall rules**: Use Ansible's `community.general.ufw` module to configure firewall rules
- **SSH hardening**: Implement SSH security settings using Ansible's `ansible.posix.sshd_config` module
- **sysctl security settings**: Use Ansible's `ansible.posix.sysctl` module to apply kernel parameters
- **Redis password**: Store Redis authentication password in Ansible Vault
- **PostgreSQL credentials**: Store database credentials in Ansible Vault
- **SSL certificates**: Ensure proper handling of SSL certificates and private keys with appropriate permissions

### Technical Challenges

- **Custom Resource Migration**: The `lineinfile` custom resource will need to be replaced with Ansible's native `lineinfile` module
- **Template Conversion**: All ERB templates need to be converted to Jinja2 format for Ansible
- **Multi-site Configuration**: Ensure the dynamic generation of multiple Nginx site configurations is properly implemented in Ansible
- **Service Dependencies**: Maintain proper service dependencies and ordering during the migration
- **SSL Certificate Generation**: Implement self-signed certificate generation using Ansible's crypto modules

### Migration Order

1. **nginx-multisite cookbook** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Implement SSL certificate generation
   - Configure virtual hosts
   - Implement security hardening

2. **cache cookbook** (Priority 2)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper integration with Nginx

3. **fastapi-tutorial cookbook** (Priority 3)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service
   - Integrate with Nginx and caching services

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based distributions
2. The Vagrant development environment will be maintained for testing
3. The current security configurations (fail2ban, ufw, SSH hardening) are required in the Ansible implementation
4. Self-signed certificates are acceptable for development/testing environments
5. The FastAPI application source code will remain available at the specified Git repository
6. The Redis password and PostgreSQL credentials will need to be securely managed in the Ansible implementation
7. The current directory structure and file paths (/opt/fastapi-tutorial, /etc/ssl/certs, etc.) should be maintained
8. The Nginx site configurations (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same