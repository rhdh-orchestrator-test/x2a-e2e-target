# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Caching services configuration with memcached and Redis, including authentication, logging, and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service management

- **nginx-multisite**:
    - Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef Solo run configuration with site-specific attributes and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules and custom configuration tasks

### Security Considerations
- **Hardcoded credentials**: Redis password and PostgreSQL credentials are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration with community.crypto collection
- **SSH hardening**: Root login disable and password authentication disable - migrate to ansible.posix.sshd_config module
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban configuration**: Custom jail.local template - migrate to community.general.fail2ban module
- **Credential patterns per module**:
  - cache: Redis requirepass in node attributes (1 password)
  - fastapi-tutorial: PostgreSQL user password and database connection string in .env file (2 credentials)
  - nginx-multisite: SSL certificate generation (multiple cert/key pairs per site)

### Technical Challenges
- **Ruby block configuration patching**: The cache cookbook uses ruby_block to modify Redis config files post-installation - requires custom Ansible tasks with lineinfile or replace modules
- **Multi-site SSL certificate generation**: Dynamic certificate creation based on site configuration - requires Ansible loops with community.crypto.openssl_* modules
- **Service dependency management**: PostgreSQL must be running before database creation - requires proper task ordering and handlers
- **Template variable mapping**: Chef ERB templates need conversion to Jinja2 with attribute mapping from Chef node attributes to Ansible variables

### Migration Order
1. **cache** (low risk, standalone caching services)
2. **nginx-multisite** (moderate complexity, security configurations)
3. **fastapi-tutorial** (high complexity, application deployment with database dependencies)

### Assumptions
- Current Chef cookbooks are actively maintained and represent the desired end state
- SSL certificates are acceptable as self-signed for development environments
- PostgreSQL and Redis passwords can be migrated to Ansible Vault without service disruption
- UFW firewall rules are appropriate for the target environment
- The multi-site configuration in solo.json represents the complete list of required sites
- Chef Solo execution model can be replaced with Ansible playbook execution
- External cookbook dependencies (nginx, memcached, redisio) functionality can be replicated with native Ansible modules
- The ruby_block configuration fixes in the cache cookbook are still necessary and not resolved in newer Redis versions