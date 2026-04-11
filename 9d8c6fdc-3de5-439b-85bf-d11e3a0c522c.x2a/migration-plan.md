# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is moderate, with security configurations and multi-site SSL management requiring careful attention. The estimated timeline for migration is 2-3 weeks for a single developer, or 1-2 weeks with a team of 2-3 members.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site-specific configurations
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

- `Berksfile`: Dependency management for Chef cookbooks, listing both local and external dependencies
- `Policyfile.rb`: Chef policy file defining the run list and cookbook dependencies
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `solo.json`: Node attributes and run list for Chef Solo, contains site configurations and security settings
- `Vagrantfile`: Defines a Fedora 42 VM for development/testing with port forwarding and network configuration
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks in the Vagrant environment

### Target Details

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) based on cookbook metadata. Development environment uses Fedora 42.
- **Virtual Machine Technology**: Vagrant with libvirt provider based on the Vagrantfile configuration.
- **Cloud Platform**: Not specified in the repository. The configuration appears to be designed for on-premises or generic cloud VMs.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct configuration
- **ssl_certificate (~> 2.1)**: Replace with Ansible's openssl_* modules for certificate management

### Security Considerations

- **SSL Certificate Management**: Migration must handle the generation and management of SSL certificates for multiple sites. Use Ansible's `openssl_certificate` module.
- **fail2ban Configuration**: The Chef cookbook configures fail2ban for intrusion prevention. Use Ansible's `template` module to create fail2ban configuration.
- **UFW Firewall Rules**: The Chef cookbook sets up UFW firewall rules. Use Ansible's `ufw` module to configure firewall rules.
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. Use Ansible's `lineinfile` or `template` modules to configure SSH.
- **Redis Authentication**: The cache cookbook sets a Redis password. Use Ansible's `template` module to configure Redis with authentication.
- **PostgreSQL User/Password**: The FastAPI cookbook creates a PostgreSQL user with password. Use Ansible's `postgresql_*` modules to manage database users securely.

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically creates Nginx site configurations based on node attributes. Ansible templates will need to replicate this dynamic behavior.
- **SSL Certificate Generation**: Self-signed certificates are generated for each site. Ansible will need to handle certificate creation and renewal.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. Ansible handlers and conditionals will need to manage these dependencies.
- **Python Environment Management**: The FastAPI application uses a Python virtual environment. Ansible's `pip` module with the `virtualenv` parameter will be needed.

### Migration Order

1. **cache cookbook** (low complexity): Start with the cache module as it has well-defined dependencies and functionality.
2. **nginx-multisite cookbook** (moderate complexity): Next, migrate the Nginx configuration as it's central to the application stack.
3. **fastapi-tutorial cookbook** (moderate complexity): Finally, migrate the application deployment which depends on both Nginx and caching services.

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS as specified in the cookbook metadata.
2. The Vagrant development environment will be maintained for testing the Ansible playbooks.
3. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment.
4. Self-signed certificates are acceptable for development; production may require integration with Let's Encrypt or other certificate authorities.
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
6. The Redis password and PostgreSQL credentials in the Chef cookbooks are development credentials and will be replaced in production.
7. The current directory structure with separate modules will be maintained in the Ansible roles.