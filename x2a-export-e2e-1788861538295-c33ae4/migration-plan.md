# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication, logging, and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis config patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL certificates, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration for all three cookbooks
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-agnostic configuration

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.template for custom Redis configuration

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH hardening**: Root login disabled, password authentication disabled - preserve these security settings
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to ansible.posix.ufw module
- **Fail2ban configuration**: Custom jail.local template - migrate template to Jinja2
- **Sysctl security tuning**: Custom kernel parameters via template - migrate to ansible.posix.sysctl

### Technical Challenges

- **Ruby block workarounds**: The cache cookbook uses ruby_block to patch Redis configuration files post-installation - this custom logic needs to be reimplemented using Ansible lineinfile or template modules
- **Multi-service coordination**: The nginx-multisite cookbook orchestrates multiple services (nginx, fail2ban, ufw, ssh) with complex notification chains - requires careful Ansible handler design
- **Template migration**: ERB templates (.erb) need conversion to Jinja2 (.j2) with syntax adjustments
- **Git repository management**: FastAPI cookbook clones and manages a Git repository - migrate to ansible.builtin.git module with proper idempotency
- **PostgreSQL user/database creation**: SQL commands executed via shell - migrate to community.postgresql.* modules for better idempotency

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached are independent services with minimal external dependencies
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database dependencies but isolated from web tier
3. **nginx-multisite** (high complexity, security-critical) - Complex security configurations and multi-service coordination, depends on application services being available

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed SSL certificates are acceptable for development environments (production may require proper CA-signed certificates)
- PostgreSQL and Redis passwords can be migrated to Ansible Vault without application code changes
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- UFW firewall is the preferred firewall solution (vs. iptables or firewalld)
- Systemd is available on target systems for service management
- The custom Redis configuration patching in the cache cookbook is still necessary and not resolved by newer Redis versions
- Development workflow using Vagrant can be replaced with molecule or similar Ansible testing frameworks