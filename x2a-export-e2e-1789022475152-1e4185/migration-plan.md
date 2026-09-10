# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis 6379 with authentication, custom log directory setup, and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis authentication (requirepass), memcached integration, Redis log directory management, configuration file post-processing

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban/UFW, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration (test/ci/status.cluster.local), SSL certificate auto-generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with attribute overrides for site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local/on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with ansible.builtin.package, custom Redis configuration templates, and service management

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH Hardening**: Root login disabled, password authentication disabled - preserve these security configurations
- **Firewall Configuration**: UFW rules for SSH (22), HTTP (80), HTTPS (443) - maintain equivalent iptables/firewalld rules
- **Fail2ban Integration**: SSH brute-force protection configured - migrate jail configurations to Ansible templates
- **Sysctl Security Tuning**: Kernel parameter hardening via /etc/sysctl.d/99-security.conf - preserve security settings

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that post-processes Redis config files to remove specific directives - this custom logic needs careful translation to Ansible lineinfile or replace modules
- **Multi-site SSL Certificate Generation**: Dynamic SSL certificate creation for multiple subdomains requires loop-based certificate generation in Ansible
- **Service Orchestration**: Complex service dependencies (PostgreSQL → FastAPI application → Nginx) require proper Ansible handler and dependency management
- **Template Variable Mapping**: Chef attributes and node data need mapping to Ansible host_vars and group_vars structure

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached have minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Security hardening and SSL setup, but well-contained functionality  
3. **fastapi-tutorial** (high complexity) - Database provisioning, application deployment, and service dependencies

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development; production may require proper CA-signed certificates
- Current hardcoded passwords are development placeholders and will be replaced with proper secret management
- The three-site configuration (test/ci/status.cluster.local) represents the complete scope of nginx virtual hosts
- PostgreSQL and Redis services will continue running on the same hosts as the applications
- UFW firewall is the preferred firewall solution (vs. iptables/firewalld alternatives)
- Systemd is available on target systems for service management
- Git repository access (https://github.com/dibanez/fastapi_tutorial.git) will remain available during migration