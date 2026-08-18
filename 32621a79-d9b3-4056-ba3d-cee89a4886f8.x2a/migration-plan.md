# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with FastAPI application backend and caching services. The migration scope includes 3 Chef cookbooks with moderate complexity. Based on the repository analysis, we estimate a 2-3 week timeline for complete migration, with the most complex components being the Nginx multi-site SSL configuration and security hardening.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: SSL certificate generation, fail2ban integration, UFW firewall configuration, multi-site hosting

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including external dependencies from Chef Supermarket. Migration will require mapping these to Ansible Galaxy roles or collections.
- `solo.json`: Contains node configuration data including site definitions and security settings. Will need to be converted to Ansible inventory variables.
- `solo.rb`: Chef configuration file that will be replaced by Ansible configuration.
- `Vagrantfile`: Development environment definition using Fedora 42. Can be adapted for Ansible testing.
- `vagrant-provision.sh`: Provisioning script for Vagrant that installs Chef. Will need to be replaced with Ansible installation.

### Target Details

Based on the source repository analysis:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module or community.general collection
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` module or community.general collection
- **redisio (~> 7.2.4)**: Replace with Ansible's `redis` module or community.redis collection

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should use Ansible's `openssl_*` modules or consider integration with Let's Encrypt via `community.crypto` collection.
- **Firewall Configuration**: UFW configuration should be migrated to Ansible's `ufw` module.
- **Fail2ban Integration**: Fail2ban configuration should be migrated using Ansible's template module.
- **SSH Hardening**: SSH security settings should be migrated using Ansible's `lineinfile` or template modules.
- **Vault/secrets management**:
  - Redis password in cache cookbook: Should be stored in Ansible Vault
  - PostgreSQL credentials in fastapi-tutorial cookbook: Should be stored in Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The current implementation uses Chef templates to generate site configurations. Ansible will need to use templates with similar logic to handle multiple sites.
- **SSL Certificate Generation**: Self-signed certificate generation will need to be replicated in Ansible using the `openssl_*` modules.
- **System Hardening**: Security configurations across multiple services will need to be carefully migrated to maintain the same security posture.
- **Service Dependencies**: The current implementation manages dependencies between services (e.g., FastAPI depends on PostgreSQL). Ansible handlers and meta dependencies will need to be configured to maintain these relationships.

### Migration Order

1. **cache cookbook** (low complexity): Simple configuration of Memcached and Redis services
2. **fastapi-tutorial cookbook** (moderate complexity): Python application deployment with PostgreSQL
3. **nginx-multisite cookbook** (high complexity): Complex multi-site configuration with SSL and security features

### Assumptions

1. The target environment will continue to be Fedora-based systems, with potential support for Ubuntu and CentOS as indicated in the cookbook metadata.
2. Self-signed certificates are acceptable for the migrated solution, rather than integrating with a certificate authority.
3. The current security posture (fail2ban, UFW, SSH hardening) should be maintained in the Ansible implementation.
4. The Vagrant development environment should be preserved with similar functionality.
5. The current Redis password and PostgreSQL credentials are development credentials and can be replaced during migration.
6. The FastAPI application source will continue to be pulled from the same Git repository.