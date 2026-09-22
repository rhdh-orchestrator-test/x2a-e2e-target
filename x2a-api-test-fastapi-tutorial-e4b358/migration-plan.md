# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW firewall, and self-signed certificate generation for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, sysctl security tuning, self-signed certificate generation

**cache**:
- Description: Caching services configuration with Redis authentication and Memcached, including custom Redis configuration fixes for compatibility
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis server with password authentication, Memcached service, custom Redis configuration patching via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Node configuration with run_list and attribute overrides for site configurations and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning (requires review for Vagrant-specific configurations)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant environment setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **ssl_certificate (~> 2.1)**: Currently commented out, replace with community.crypto.openssl_* modules for certificate management

### Security Considerations

- **Hardcoded Credentials**: Redis password 'redis_secure_password_123' and PostgreSQL password 'fastapi_password' are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - migrate to community.crypto collection for proper certificate lifecycle management
- **SSH Security Configuration**: Root login disabled and password authentication disabled via direct file manipulation - migrate to ansible.posix.sshd_config module
- **Firewall Rules**: UFW firewall rules managed via shell commands - migrate to community.general.ufw module
- **Fail2ban Configuration**: Template-based jail configuration - migrate to community.general.fail2ban module

### Technical Challenges

- **Ruby Block Workarounds**: The cache cookbook contains a ruby_block hack to fix Redis configuration by removing specific lines - this custom logic needs to be replicated in Ansible using lineinfile or template modules
- **Service Dependencies**: Complex service startup order (PostgreSQL before FastAPI, nginx after SSL certificates) requires careful Ansible handler and dependency management
- **Git Repository Management**: FastAPI application deployment via git clone needs migration to ansible.builtin.git module with proper change detection
- **Template Variable Mapping**: ERB templates need conversion to Jinja2 with variable name mapping from Chef attributes to Ansible variables

### Migration Order

1. **cache** (low risk, high value): Simple service installation with well-defined external dependencies
2. **fastapi-tutorial** (moderate complexity): Application deployment with database setup, manageable scope
3. **nginx-multisite** (high complexity, dependencies): Complex multi-site configuration with security hardening, depends on understanding application requirements

### Assumptions

- Target environment will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments (production may require Let's Encrypt or CA-signed certificates)
- Current hardcoded passwords are acceptable for migration (should be moved to Ansible Vault post-migration)
- Vagrant development environment will be replaced with equivalent Ansible-based provisioning
- External cookbook dependencies (nginx, memcached, redisio) functionality can be replicated with native Ansible modules
- Ruby_block workarounds in Redis configuration indicate potential compatibility issues that may need investigation in target environment
- Site-specific static files (index.html for test/ci/status sites) will be managed through Ansible file or template modules
- Current systemd service configuration approach is suitable for target environment