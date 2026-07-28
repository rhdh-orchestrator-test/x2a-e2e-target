# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks. The estimated complexity is moderate, with security configurations and SSL certificate management requiring special attention.

**Timeline Estimate:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, fail2ban integration, UFW firewall setup, security headers

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration file for development environment setup

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role or the `ansible.builtin.package` module
- **memcached (~> 6.0)**: Replace with Ansible `memcached` role or custom role using `ansible.builtin.package` and templates
- **redisio (~> 7.2.4)**: Replace with Ansible `redis` role or custom role using `ansible.builtin.package` and templates

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. In Ansible, use the `community.crypto.openssl_*` modules for certificate generation or consider integrating with Let's Encrypt using `community.crypto.acme_*` modules.
- **Firewall Configuration**: The current implementation uses UFW. In Ansible, use the `ansible.posix.firewalld` module for RHEL/Fedora or `community.general.ufw` module for Ubuntu.
- **fail2ban Integration**: Use the `community.general.fail2ban` module to configure fail2ban in Ansible.
- **SSH Hardening**: The current implementation disables root login and password authentication. In Ansible, use the `ansible.posix.sshd_config` module to manage SSH configuration.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - Consider using Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: The current implementation uses ERB templates with complex conditionals. In Ansible, create Jinja2 templates with equivalent logic and use `with_items` loops to process multiple sites.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. In Ansible, use handlers and the `meta: flush_handlers` directive to ensure services start in the correct order.
- **Redis Configuration**: The current implementation includes a Ruby block to modify Redis configuration. In Ansible, use the `ansible.builtin.lineinfile` or `ansible.builtin.template` module with proper templates.
- **Python Environment Management**: The current implementation creates and configures a Python virtual environment. In Ansible, use the `ansible.builtin.pip` module with the `virtualenv` parameter.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement security configurations (fail2ban, firewall)
   - Configure virtual hosts

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database
   - Deploy application code
   - Configure Python environment
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (the Vagrantfile specifies Fedora 42).
2. Self-signed certificates are acceptable for the migrated solution (production environments might require proper CA-signed certificates).
3. The security requirements (fail2ban, firewall, SSH hardening) will remain the same.
4. The application deployment strategy (cloning from Git) will remain unchanged.
5. The database credentials and Redis password will need to be securely managed in the Ansible solution.
6. The current Chef implementation does not use encrypted data bags or other secret management, so all secrets are currently stored in plaintext.
7. The Vagrant development environment will be maintained for testing the Ansible playbooks.