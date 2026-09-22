# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a Python FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to multi-service dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and self-signed certificate generation for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, sysctl security tuning

**cache**:
- Description: Caching services configuration providing both Memcached and Redis with authentication, custom Redis configuration patching, and log directory management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis 6379 with password authentication, Memcached service, Redis configuration file manipulation via Ruby blocks, custom log directory setup

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service management, environment configuration file generation

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configurations and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning for testing
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with ansible.builtin.package, custom Redis configuration tasks, and ansible.builtin.service modules

### Security Considerations

- **Hardcoded Credentials**: Multiple hardcoded passwords identified requiring Ansible Vault migration:
  - Redis password: 'redis_secure_password_123' in cache cookbook
  - PostgreSQL password: 'fastapi_password' in fastapi-tutorial cookbook
  - Database connection strings with embedded credentials in .env files
- **SSL Certificate Management**: Self-signed certificate generation for development environments needs conversion to ansible.builtin.openssl_* modules
- **SSH Hardening**: Root login disable and password authentication disable configurations need migration to ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules and fail2ban jail configurations require migration to ansible.posix.ufw and community.general.fail2ban modules
- **File Permissions**: SSL private key permissions (640, ssl-cert group) need careful migration to maintain security posture

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains complex Ruby block manipulation of Redis configuration files that will need conversion to Ansible lineinfile or template modules
- **Service Dependencies**: Multi-service startup dependencies (PostgreSQL before FastAPI, nginx after SSL certificates) require careful Ansible handler and dependency management
- **Template Conversion**: ERB templates need conversion to Jinja2 format, particularly nginx.conf.erb and security configuration templates
- **Attribute Hierarchy**: Chef attribute precedence and node attribute overrides in solo.json need mapping to Ansible variable precedence and group_vars structure

### Migration Order

1. **cache cookbook** (low risk, standalone service, good starting point for Ruby block conversion patterns)
2. **nginx-multisite cookbook** (moderate complexity, establishes security and SSL patterns for other services)
3. **fastapi-tutorial cookbook** (highest complexity, depends on database setup and application deployment patterns)

### Assumptions

- Target environments will maintain the same OS distributions (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments; production may require Let's Encrypt or CA-signed certificates
- Current hardcoded passwords are development/testing credentials and will be replaced with proper secret management
- The Ruby block Redis configuration manipulation is a workaround for cookbook limitations and can be replaced with proper Redis configuration management
- UFW and fail2ban are the preferred security tools and should be maintained in the Ansible migration
- PostgreSQL database initialization and user creation patterns are suitable for the target environment
- Git repository access for FastAPI tutorial code will remain available during and after migration
- Systemd is the target service manager for all services (FastAPI, nginx, Redis, Memcached)
- The multi-site nginx configuration pattern (test.cluster.local, ci.cluster.local, status.cluster.local) represents the desired production architecture