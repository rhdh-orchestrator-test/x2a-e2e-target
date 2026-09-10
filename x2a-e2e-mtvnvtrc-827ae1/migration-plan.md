# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with SSL and security hardening. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation via external cookbook, Redis with password authentication, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

**nginx-multisite**:
- Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, and SSH configuration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration with self-signed certificates, fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning (likely for testing)
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificate generation for development environments - consider Let's Encrypt integration for production
- **SSH Hardening**: Root login disabled, password authentication disabled - preserve these security configurations
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to ansible.posix.ufw module
- **Fail2ban Integration**: Intrusion prevention with custom jail configuration - migrate to community.general.fail2ban module
- **Credential Patterns per Module**:
  - cache: Redis authentication password (hardcoded string)
  - fastapi-tutorial: PostgreSQL database credentials (hardcoded strings), application environment variables
  - nginx-multisite: SSL certificate paths, no embedded credentials but certificate generation

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this will need custom Ansible tasks with lineinfile or replace modules
- **Multi-site SSL Management**: Dynamic SSL certificate generation for multiple sites based on node attributes - requires Ansible loops and conditional logic
- **External Cookbook Dependencies**: Three external Chef cookbooks need equivalent Ansible roles or custom implementations
- **Service Orchestration**: Complex service dependencies (PostgreSQL → FastAPI application, SSL certificates → Nginx) require careful task ordering and handlers

### Migration Order

1. **cache** (moderate complexity, standalone service)
2. **nginx-multisite** (high complexity due to SSL and security features, but foundational)
3. **fastapi-tutorial** (depends on database setup, integrates with nginx for complete stack)

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in Chef metadata
- Self-signed certificates are acceptable for development; production may require different certificate management
- Current hardcoded passwords are development placeholders and will be replaced with proper secret management
- The Ruby-based Redis configuration patching indicates potential compatibility issues that may not exist in target environments
- Vagrant development workflow will be preserved or replaced with equivalent Ansible testing methodology
- External cookbook versions (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) represent stable, well-tested configurations that should be replicated in Ansible equivalents