# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI application with PostgreSQL backend. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and self-signed certificate generation for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL termination, fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, sysctl security tuning, self-signed certificate generation

**cache**:
- Description: Caching layer services providing both Redis (with authentication) and Memcached instances for application performance optimization
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis 6379 with password authentication, Memcached service, custom Redis configuration cleanup, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service integration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user provisioning, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with cookbook execution order and attribute overrides for site configurations
- `solo.rb`: Chef Solo configuration file (likely contains cookbook paths and cache settings)
- `Vagrantfile`: Development environment provisioning for local testing
- `vagrant-provision.sh`: Shell script for Vagrant VM initialization

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be platform-agnostic configuration

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or ansible.builtin.package for memcached installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package with custom configuration templates

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH Security Configuration**: Root login disabled, password authentication disabled - migrate using ansible.posix.sshd_config module
- **Firewall Rules**: UFW configuration for ports 22, 80, 443 - migrate using community.general.ufw module
- **Fail2ban Configuration**: Intrusion prevention via template-based jail.local - migrate using ansible.builtin.template with community.general.fail2ban module
- **Credential Types Per Module**:
  - nginx-multisite: SSL certificate paths, no embedded secrets
  - cache: Redis authentication password (hardcoded)
  - fastapi-tutorial: PostgreSQL database credentials (hardcoded), application environment variables

### Technical Challenges

- **Redis Configuration Cleanup**: The cache cookbook contains a Ruby block hack to remove specific Redis configuration lines - this custom logic needs careful translation to Ansible lineinfile or replace modules
- **Multi-site SSL Certificate Generation**: Dynamic certificate creation per site requires Ansible loops with community.crypto modules
- **Service Dependencies**: PostgreSQL must be running before FastAPI application starts - requires proper Ansible handler ordering and service dependencies
- **Git Repository Management**: FastAPI cookbook clones from GitHub - ensure Ansible control node has git access and consider using ansible.builtin.git module with proper authentication
- **Python Virtual Environment**: Complex pip installation within venv requires ansible.builtin.pip module with proper virtualenv parameters

### Migration Order

1. **cache** (low risk, high value): Simple service installation with clear dependencies, provides immediate performance benefits
2. **nginx-multisite** (moderate complexity): Core infrastructure component, security hardening can be implemented incrementally
3. **fastapi-tutorial** (high complexity, dependencies): Requires cache and nginx to be operational, complex application deployment with database dependencies

### Assumptions

- Current Chef cookbooks target Ubuntu/CentOS environments - Ansible playbooks will maintain same OS compatibility
- Self-signed certificates are acceptable for development - production deployment may require Let's Encrypt or CA-signed certificates
- PostgreSQL and Redis passwords are development-only credentials - production secrets will be managed via Ansible Vault
- Git repository access (https://github.com/dibanez/fastapi_tutorial.git) remains available and accessible from Ansible control node
- Systemd is available on target systems for service management (implied by Ubuntu 18.04+ and CentOS 7+ support)
- Network connectivity allows package installation from default repositories (nginx, postgresql, python3, etc.)
- Target systems have sufficient disk space for application code, logs, and database storage
- Current site configurations (test.cluster.local, ci.cluster.local, status.cluster.local) represent actual target hostnames or will be updated during migration