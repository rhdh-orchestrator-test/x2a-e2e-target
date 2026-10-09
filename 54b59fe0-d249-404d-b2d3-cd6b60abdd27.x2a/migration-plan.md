# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a Python FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication, custom log directory setup, and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication (redis_secure_password_123), memcached integration, Redis configuration file manipulation via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file with database credentials

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local), SSL certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management with external dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and attribute overrides for site configurations and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning for testing cookbook deployments
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning and Chef Solo execution

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata.rb supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence for development)
- **Cloud Platform**: Not specified (local development environment focus)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificate generation for three domains requires migration to ansible.builtin.openssl_* modules
- **SSH Hardening**: Root login disable and password authentication disable need migration to ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH require migration to community.general.ufw module
- **Fail2ban Configuration**: Jail configuration template needs migration to ansible.builtin.template module
- **Credential Types per Module**:
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables
  - nginx-multisite: SSL certificate generation (self-signed), no external credential dependencies

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook uses a ruby_block to manipulate Redis configuration files post-installation - requires conversion to ansible.builtin.lineinfile or ansible.builtin.replace modules
- **Complex Site Configuration**: nginx-multisite manages multiple virtual hosts with dynamic SSL certificate generation - needs careful mapping to Ansible loops and conditionals
- **Service Dependencies**: PostgreSQL must be running before database/user creation in fastapi-tutorial - requires proper Ansible task ordering and handlers
- **Template Migration**: ERB templates (.erb) need conversion to Jinja2 templates (.j2) with syntax adjustments
- **File Resource Management**: Chef cookbook_file resources need migration to ansible.builtin.copy or ansible.builtin.template modules

### Migration Order

1. **cache** (low risk, high value): Simple package installation and service management with minimal external dependencies
2. **fastapi-tutorial** (moderate complexity): Application deployment with database setup, manageable service configuration
3. **nginx-multisite** (high complexity, dependencies): Complex multi-site configuration with security hardening, SSL management, and firewall rules

### Assumptions

- Target systems will maintain the same OS family (Ubuntu/CentOS) as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (no Let's Encrypt or CA-signed certificate requirements identified)
- PostgreSQL and Redis will continue to run on the same hosts as the applications (no database server separation identified)
- The three nginx virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local) represent the complete site configuration requirements
- Current hardcoded passwords are acceptable for migration to Ansible Vault (no password rotation requirements specified)
- UFW firewall is the preferred firewall solution (no iptables or firewalld requirements identified)
- Systemd is available on target systems for service management (based on fastapi-tutorial systemd service configuration)
- The Git repository https://github.com/dibanez/fastapi_tutorial.git will remain accessible during and after migration
- Development/testing will continue to use Vagrant-based environments until Ansible equivalents are established