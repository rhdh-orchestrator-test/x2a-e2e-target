# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site configuration, security hardening via fail2ban/UFW firewall, and SSH security controls
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Self-signed SSL certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening (root login disabled, password auth disabled), sysctl security tuning, multiple virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local)

**cache**:
- Description: Caching services configuration with Redis authentication and Memcached setup, including Redis configuration workarounds
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis server with password authentication (requirepass), custom log directory creation, configuration file manipulation via ruby_block, Memcached integration, Redis service enablement

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning from GitHub, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment variable management (.env file)

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo node configuration with run_list and attribute overrides for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file (likely contains cookbook paths and cache settings)
- `Vagrantfile`: Development environment provisioning configuration for local testing
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning automation

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence for development)
- **Cloud Platform**: Not specified (local development focus with potential for cloud deployment)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and ansible.builtin.template for configuration
- **Chef Solo**: Replace with Ansible playbooks and inventory management
- **Berkshelf**: Replace with Ansible Galaxy and requirements.yml for external role dependencies

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration with community.crypto.acme_certificate
- **SSH Security Configuration**: Root login disabled and password authentication disabled via sed commands - migrate to ansible.posix.sshd_config module
- **Firewall Rules**: UFW commands executed directly - migrate to community.general.ufw module
- **Database Credentials**: PostgreSQL user/password creation via shell commands - migrate to community.postgresql.postgresql_* modules with vault integration
- **Environment Variables**: FastAPI .env file contains database connection strings - secure with ansible-vault

### Technical Challenges

- **Ruby Block Workarounds**: The cache cookbook contains a ruby_block that manipulates Redis configuration files with regex replacements - this indicates upstream cookbook limitations that need clean Ansible template solutions
- **Service Dependencies**: Complex service startup order (PostgreSQL → FastAPI, nginx → SSL certificates) requires careful Ansible handler and dependency management
- **Git Repository Integration**: FastAPI cookbook clones from GitHub with potential authentication needs - migrate to ansible.builtin.git with proper credential handling
- **Multi-Site SSL**: Self-signed certificate generation for multiple domains requires loop-based certificate creation in Ansible
- **Package Installation Variations**: Different package names across Ubuntu/CentOS require conditional package installation logic

### Migration Order

1. **cache** (low risk, foundational service) - Redis and Memcached are well-supported in Ansible with stable modules
2. **nginx-multisite** (moderate complexity) - Security configurations and SSL management require careful testing
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies and service management

### Assumptions

- SSL certificates are currently self-signed for development; production deployment may require different certificate management strategy
- Redis configuration workarounds in ruby_block suggest potential issues with the redisio cookbook that may not exist in Ansible redis modules
- PostgreSQL database creation assumes local installation; cloud database services may require different connection patterns
- UFW firewall rules assume Ubuntu/Debian systems; CentOS support may require firewalld alternative
- Git repository access to https://github.com/dibanez/fastapi_tutorial.git assumes public access; private repositories need credential configuration
- Current Chef Solo deployment suggests single-node architecture; multi-node deployments would require inventory and group variable restructuring
- Vagrant development environment indicates local testing workflow that should be preserved in Ansible migration
- SSH security settings assume password-based authentication is currently enabled and needs to be disabled post-migration