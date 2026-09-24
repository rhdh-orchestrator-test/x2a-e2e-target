# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with security hardening. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service management

**nginx-multisite**:
- Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration, SSL certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local/on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificate generation for development environments - consider Let's Encrypt integration for production
- **SSH Hardening**: Root login disable and password authentication disable configurations need careful migration
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH ports require equivalent iptables or firewalld Ansible modules
- **Fail2ban Configuration**: Jail configurations in ERB templates need conversion to Jinja2 templates
- **Credential Types per Module**:
  - cache: Redis authentication password (hardcoded)
  - fastapi-tutorial: PostgreSQL database credentials (hardcoded)
  - nginx-multisite: SSL certificate generation (self-signed, no external secrets)

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains a ruby_block that performs complex Redis configuration file manipulation - requires conversion to Ansible lineinfile or replace modules with regex patterns
- **Chef Resource Dependencies**: Complex notification chains between templates, services, and execute resources need careful conversion to Ansible handlers
- **Multi-Site Template Logic**: ERB templates with Chef node attributes iteration need conversion to Jinja2 with Ansible variables
- **Package Installation Coordination**: Chef's package resource arrays need conversion to Ansible package loops or individual tasks
- **Service Management**: Chef's service resource with complex support options requires mapping to Ansible service module equivalents

### Migration Order

1. **nginx-multisite** (moderate complexity, foundational web server)
2. **cache** (low-medium complexity, but contains ruby_block challenge)
3. **fastapi-tutorial** (highest complexity due to application deployment and database setup)

### Assumptions

- Current Chef cookbooks are actively used and represent the desired end state configuration
- External cookbook dependencies (nginx, memcached, redisio) can be replaced with equivalent Ansible modules or community roles
- Self-signed SSL certificates are acceptable for the target environment (development/testing)
- PostgreSQL and Redis services will continue to run on the same hosts as the applications
- UFW firewall is the preferred firewall solution (vs. iptables/firewalld)
- Systemd is available on target systems for service management
- The Vagrant development workflow should be preserved with Ansible provisioning
- Git repository access for FastAPI tutorial code will remain available during migration
- Current hardcoded passwords are acceptable for development but should be vaulted for production use