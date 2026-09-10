# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and maintaining security configurations including fail2ban, UFW firewall, and SSL certificate management.

**Estimated Timeline**: 4-6 weeks for complete migration
**Complexity**: Medium - straightforward service configurations with some security hardening
**Team Coordination**: Requires coordination between application, infrastructure, and security teams

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configurations and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning for testing
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be generic Linux deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH Hardening**: Root login disabled, password authentication disabled - maintain with ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **Fail2ban Configuration**: Custom jail.local template - migrate template to Ansible with community.general.fail2ban module
- **Sysctl Security**: Custom kernel parameter tuning - migrate to ansible.posix.sysctl module
- **Credential Types per Module**:
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables
  - nginx-multisite: SSL certificate generation (self-signed)

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this will need to be replicated using Ansible lineinfile or template modules
- **Multi-site SSL Management**: Dynamic SSL certificate generation for multiple sites based on node attributes - requires Ansible loops and conditional logic
- **Service Dependencies**: PostgreSQL must be running before FastAPI application starts - ensure proper task ordering and handlers in Ansible
- **Template Migration**: ERB templates need conversion to Jinja2 format, particularly nginx.conf.erb and security configuration templates

### Migration Order

1. **cache** (low risk, standalone service) - Start with caching services as they have minimal dependencies
2. **nginx-multisite** (moderate complexity) - Core infrastructure component with security configurations
3. **fastapi-tutorial** (highest complexity) - Application deployment with database dependencies and service management

### Assumptions

- The target environment will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (production deployments may require CA-signed certificates)
- The hardcoded passwords in the Chef recipes are development/testing credentials and will be replaced with proper secret management in Ansible Vault
- The custom Redis configuration patching in the cache cookbook is still required in the target environment
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible and the main branch will be used
- UFW firewall and fail2ban are the preferred security tools for the target environment
- The multi-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the actual target domains
- Systemd is available on the target systems for service management
- The current Chef Solo execution model will be replaced with standard Ansible playbook execution