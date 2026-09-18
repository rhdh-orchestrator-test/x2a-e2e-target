# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to multi-service dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and self-signed certificate generation for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, sysctl security tuning, self-signed certificate generation

**cache**:
- Description: Caching services configuration providing both memcached and Redis with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service setup, Redis 6379 with password authentication, custom Redis configuration patching via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment setup, Git repository cloning from GitHub, PostgreSQL database and user creation, systemd service management, environment configuration file management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configuration and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning for testing
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached module or direct package/service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and ansible.builtin.lineinfile for configuration management

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate using ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate using community.general.ufw module
- **Fail2ban Configuration**: Intrusion prevention via template - migrate using ansible.builtin.template with fail2ban configuration
- **Credential Types per Module**:
  - nginx-multisite: SSL certificate paths, no embedded secrets
  - cache: Redis authentication password (hardcoded)
  - fastapi-tutorial: PostgreSQL database credentials (hardcoded), GitHub repository access (public)

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook uses a ruby_block to patch Redis configuration files post-installation - requires conversion to Ansible lineinfile or replace modules with proper regex patterns
- **Multi-Site SSL Management**: Dynamic SSL certificate generation for multiple sites requires Ansible loops and conditional logic based on site configuration
- **Service Dependencies**: FastAPI service depends on PostgreSQL being ready - requires proper Ansible handlers and service dependency management
- **Template Complexity**: Multiple ERB templates need conversion to Jinja2 format, particularly nginx.conf and security configurations
- **Package Management**: Cross-platform support (Ubuntu/CentOS) requires conditional package management based on ansible_os_family

### Migration Order

1. **cache** (low risk, foundational service) - Redis and memcached are standalone services with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server with security configurations, depends on SSL certificate generation
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, systemd service management, and Git integration

### Assumptions

- SSL certificates are self-signed for development environments - production deployment may require Let's Encrypt or CA-signed certificates
- PostgreSQL installation uses default package repositories - specific version requirements not specified in cookbook
- Redis configuration patching via ruby_block suggests upstream cookbook limitations - may indicate need for custom Redis configuration management
- UFW firewall rules assume standard HTTP/HTTPS ports - custom application ports may need additional configuration
- Git repository access is public (no authentication specified) - private repositories would require credential management
- Systemd is the target init system - SysV or other init systems not supported
- Chef Solo execution model suggests single-node deployment - multi-node orchestration requirements unclear
- Development environment uses Vagrant - production deployment method not specified in repository