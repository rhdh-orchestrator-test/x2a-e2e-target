# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis authentication, includes Redis log directory setup and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached integration, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service management, environment file with database credentials

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban/UFW, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local), SSL certificate auto-generation, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and attribute overrides for site configurations and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning (likely contains VM configuration)
- `vagrant-provision.sh`: Shell script for Vagrant VM setup and Chef Solo execution

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in metadata.rb files)
- **Virtual Machine Technology**: Vagrant-based development environment (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local/on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and memcached configuration via templates
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Multiple credential patterns identified requiring Ansible Vault migration:
  - Redis password: `redis_secure_password_123` (hardcoded in cache cookbook)
  - PostgreSQL credentials: `fastapi:fastapi_password` (hardcoded in fastapi-tutorial cookbook)
  - Database URL with embedded credentials in .env file
- **SSL Certificate Management**: Self-signed certificate generation per subdomain requires migration to community.crypto.openssl_* modules
- **SSH Hardening**: Root login disable and password authentication disable via sshd_config modifications
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH ports need migration to community.general.ufw module
- **Fail2ban Integration**: Jail configuration template requires migration to community.general.fail2ban module
- **Sysctl Security Tuning**: Kernel parameter hardening via /etc/sysctl.d/ configuration

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains complex Ruby logic for Redis configuration file patching that needs conversion to Ansible lineinfile/replace modules
- **Multi-Site SSL Management**: Dynamic SSL certificate generation per site requires loop-based Ansible tasks with proper certificate validation
- **Service Dependencies**: PostgreSQL must be running before FastAPI application deployment, requiring proper task ordering and handlers
- **Template Migration**: ERB templates (nginx.conf.erb, security.conf.erb, site.conf.erb) need conversion to Jinja2 format
- **File Resource Complexity**: Multiple file resources with specific ownership/permissions require careful migration to ansible.builtin.file and ansible.builtin.template modules

### Migration Order

1. **cache** (low risk, standalone service)
   - Migrate memcached and Redis installation
   - Convert Ruby block logic to Ansible tasks
   - Implement credential management via Ansible Vault

2. **nginx-multisite** (moderate complexity, foundational service)
   - Migrate nginx installation and configuration templates
   - Implement SSL certificate generation loop
   - Convert security hardening tasks (fail2ban, UFW, SSH, sysctl)

3. **fastapi-tutorial** (high complexity, application dependencies)
   - Migrate Python application deployment
   - Convert PostgreSQL database provisioning
   - Implement systemd service management
   - Ensure proper dependency on nginx-multisite for reverse proxy

### Assumptions

- Chef Solo execution model suggests single-node deployment - Ansible playbooks should target individual hosts rather than orchestrated multi-node deployment
- Self-signed certificates indicate development/testing environment - production migration may require Let's Encrypt or corporate CA integration
- Hardcoded passwords suggest development environment - production deployment will require external secret management integration
- Ubuntu/CentOS support indicates need for OS-specific package management and service handling in Ansible tasks
- Vagrant development workflow suggests need for ansible-playbook integration with existing VM provisioning process
- No Chef Server dependency simplifies migration - no need to replicate Chef Server functionality in Ansible Tower/AWX
- Static site content (index.html files) suggests simple web serving - no complex application deployment patterns to migrate
- Local cookbook paths in Berksfile indicate self-contained repository - no external cookbook dependencies to resolve beyond Supermarket cookbooks