# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with security hardening. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis 6379 with authentication, custom log directory setup, and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication (redis_secure_password_123), memcached integration, Redis log directory management, configuration file manipulation via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening via fail2ban/UFW, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration (test/ci/status.cluster.local), SSL certificate generation, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run_list and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning (likely for testing)
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password 'redis_secure_password_123' and PostgreSQL password 'fastapi_password' are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate using ansible.posix.sysctl and lineinfile modules
- **Firewall Configuration**: UFW rules for SSH/HTTP/HTTPS - migrate using community.general.ufw module
- **Fail2ban Integration**: Jail configuration via template - migrate using ansible.builtin.template module
- **Credential Types per Module**:
  - cache: Redis authentication password (1 hardcoded credential)
  - fastapi-tutorial: PostgreSQL database password (1 hardcoded credential)
  - nginx-multisite: SSL certificate generation (self-signed, no stored credentials)

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook uses ruby_block to manipulate Redis configuration files post-installation - requires conversion to Ansible lineinfile or replace modules with regex patterns
- **Complex SSL Certificate Generation**: Multi-site SSL certificate generation with proper file permissions and ownership - needs careful conversion to community.crypto modules
- **Service Dependencies**: PostgreSQL must be running before database/user creation in fastapi-tutorial - requires proper Ansible task ordering and handlers
- **Template Conversion**: ERB templates (.erb files) need conversion to Jinja2 format for nginx.conf, security.conf, and fail2ban configurations
- **Git Repository Management**: FastAPI cookbook clones and manages git repositories - requires ansible.builtin.git module with proper change detection

### Migration Order

1. **cache** (low risk, standalone caching services)
2. **nginx-multisite** (moderate complexity, security configurations but well-isolated)
3. **fastapi-tutorial** (high complexity, database dependencies and application deployment)

### Assumptions

- Target systems will have internet access for package installation and git repository cloning
- PostgreSQL service management approach (systemd vs other init systems) needs clarification for different target OS families
- SSL certificate requirements in production may differ from self-signed development certificates
- The specific versions of external Chef cookbooks (nginx 12.0, memcached 6.0, redisio 7.2.4) and their feature compatibility with Ansible equivalents need verification
- UFW firewall is the preferred firewall solution (vs iptables/firewalld on different distributions)
- The ruby_block configuration patching in the cache cookbook suggests potential compatibility issues with Redis versions that may need investigation
- Vagrant development environment setup may need equivalent Ansible testing framework (molecule, vagrant with ansible provisioner, etc.)
- File ownership and permission requirements (www-data user/group, ssl-cert group) may vary across target operating systems