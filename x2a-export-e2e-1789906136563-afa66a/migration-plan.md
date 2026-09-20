# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with Redis authentication and Memcached setup, includes Redis log directory management and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, Memcached integration, custom Redis configuration fixes via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv setup, PostgreSQL database/user creation, systemd service management, environment file configuration

**nginx-multisite**:
- Description: Nginx web server with SSL-enabled multi-site hosting, comprehensive security hardening including fail2ban, UFW firewall, and SSH security configurations
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL certificate generation, multi-site virtual hosts, security headers, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo run configuration with run_list and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration specifying cookbook paths and logging settings
- `Vagrantfile`: Development environment provisioning (requires review for Vagrant-specific configurations)
- `vagrant-provision.sh`: Shell provisioning script for development setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations). Default to Red Hat Enterprise Linux 9 for production deployment.
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom configuration tasks
- **ssl_certificate (~> 2.1)**: Currently commented out, replace with community.crypto.openssl_* modules for SSL certificate management

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" in cache cookbook requires migration to Ansible Vault
- **PostgreSQL credentials**: FastAPI database password "fastapi_password" hardcoded in recipe, needs Vault integration
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands, migrate to community.crypto collection
- **SSH security configurations**: Root login disabled, password authentication disabled via direct file editing
- **Firewall rules**: UFW configuration with specific port allowances (22, 80, 443)
- **Fail2ban integration**: Custom jail.local configuration for nginx protection
- **Security headers**: Comprehensive HTTP security headers in nginx configuration
- **File permissions**: Specific ownership and permission patterns for SSL certificates and application files

### Technical Challenges

- **Ruby block configuration patching**: The cache cookbook uses a ruby_block to manually edit Redis configuration files, requiring conversion to Ansible lineinfile or template modules
- **Complex nginx templating**: Multi-conditional ERB templates with SSL/non-SSL variants need conversion to Jinja2 templates
- **Service dependency management**: PostgreSQL must be running before database user creation, requiring proper Ansible task ordering
- **Git repository management**: FastAPI cookbook clones from GitHub, needs ansible.builtin.git module with proper authentication handling
- **Systemd service creation**: Custom service files require template conversion and systemd module integration
- **Multi-site SSL certificate generation**: Dynamic certificate creation per site requires loop-based task execution

### Migration Order

1. **cache** (Priority 1): Standalone caching services with clear dependencies, good starting point for Redis/Memcached patterns
2. **fastapi-tutorial** (Priority 2): Application deployment with database dependencies, moderate complexity with systemd integration
3. **nginx-multisite** (Priority 3): Most complex with security hardening, SSL management, and multi-site configuration requiring comprehensive testing

### Assumptions

- Target environment will use systemd for service management (based on systemd service file creation in fastapi-tutorial)
- SSL certificates will remain self-signed for development environments (production may require Let's Encrypt or CA-signed certificates)
- PostgreSQL installation method may need adjustment based on target OS package availability
- UFW firewall is acceptable for target environment (may need iptables alternative for some distributions)
- Git repository access for FastAPI tutorial will remain public (private repositories require SSH key or token management)
- Redis and Memcached versions in target repositories are compatible with cookbook expectations
- Network connectivity allows access to external package repositories and GitHub
- Target systems have sufficient disk space for Python virtual environments and application files
- SSH service name consistency across target operating systems (may be 'sshd' vs 'ssh')