# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with SSL and security hardening. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external cookbook dependencies, and migrating configuration management patterns. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation via external cookbook, Redis with password authentication, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

**nginx-multisite**:
- Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local), SSL certificate management, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site-specific overrides
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local/on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.template for custom Redis configuration

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.openssl_* modules
- **SSH Hardening**: Root login and password authentication disabled via sed commands - migrate to ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules managed via shell commands - migrate to community.general.ufw module
- **Fail2ban Configuration**: Template-based jail configuration - migrate to ansible.builtin.template with Jinja2
- **Credential Types per Module**:
  - cache: Redis authentication password (hardcoded)
  - fastapi-tutorial: PostgreSQL database credentials (hardcoded)
  - nginx-multisite: SSL certificate generation (self-signed, no external secrets)

### Technical Challenges

- **Custom Redis Configuration Patching**: The cache cookbook uses a Ruby block to modify Redis config files post-installation - requires careful translation to Ansible lineinfile or template modules
- **Multi-Site SSL Certificate Generation**: Dynamic certificate creation per site requires Ansible loops and conditional logic
- **Service Dependencies**: PostgreSQL must be running before database creation, nginx must reload after configuration changes - requires proper Ansible handlers and task ordering
- **File Permissions and Ownership**: Complex permission schemes (ssl-cert group, specific directory modes) need careful mapping to Ansible file modules
- **Git Repository Integration**: FastAPI application deployment from Git requires ansible.builtin.git module with proper change detection

### Migration Order

1. **nginx-multisite** (moderate complexity, foundational web server)
2. **cache** (low complexity, but requires custom Redis configuration handling)
3. **fastapi-tutorial** (high complexity, application deployment with database dependencies)

### Assumptions

- Current Chef cookbooks are actively used in production environments
- Target systems will maintain the same OS distributions (Ubuntu 18.04+, CentOS 7+)
- Vagrant development workflow will be replaced with ansible-playbook local execution or molecule testing
- External cookbook dependencies (nginx, memcached, redisio) functionality will be replicated using native Ansible modules
- SSL certificates will remain self-signed for development; production may require Let's Encrypt or CA-signed certificates
- Database credentials and Redis passwords will be migrated to Ansible Vault for security
- The multi-site nginx configuration pattern (test.cluster.local, ci.cluster.local, status.cluster.local) will be preserved
- UFW and fail2ban security configurations are required in the target environment
- Python virtual environment management approach will be maintained for the FastAPI application
- Systemd service management is available on target systems