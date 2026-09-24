# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configuration and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-agnostic configuration

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules and custom configuration management

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificate generation with OpenSSL commands - consider community.crypto.x509_certificate module
- **SSH Hardening**: Root login disable and password authentication disable via sed commands - use ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules managed via shell commands - use community.general.ufw module
- **Fail2ban Configuration**: Template-based jail configuration - use community.general.fail2ban module
- **Credential Types per Module**:
  - cache: Redis authentication password (hardcoded)
  - fastapi-tutorial: PostgreSQL database credentials (hardcoded)
  - nginx-multisite: SSL certificate generation (self-signed, no stored secrets)

### Technical Challenges

- **Custom Redis Configuration Patching**: The cache cookbook uses Ruby blocks to modify Redis config files post-installation - requires custom Ansible tasks with lineinfile or replace modules
- **Multi-site SSL Certificate Generation**: Dynamic certificate creation per site requires loop-based certificate generation with proper file permissions
- **Service Orchestration**: Complex service dependencies (PostgreSQL → FastAPI → Nginx) require careful ordering and handler management
- **Template Migration**: ERB templates need conversion to Jinja2 format with variable mapping
- **Git Repository Management**: FastAPI cookbook clones and manages git repositories - use ansible.builtin.git module with proper change detection

### Migration Order

1. **cache** (low risk, standalone service)
2. **nginx-multisite** (moderate complexity, security-focused)
3. **fastapi-tutorial** (high complexity, database dependencies, service orchestration)

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in Chef metadata
- Self-signed certificates are acceptable for the target environment (no Let's Encrypt or CA integration required)
- Redis and PostgreSQL passwords can be migrated to Ansible Vault without changing the actual credential values
- The custom Redis configuration patching logic is still required in the target environment
- UFW firewall is the preferred firewall solution (no migration to firewalld planned)
- Systemd is available on target systems for service management
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and unchanged
- Development workflow using Vagrant will be maintained or replaced with equivalent local testing approach
- No external Chef Server integration exists (Chef Solo configuration indicates standalone deployment)