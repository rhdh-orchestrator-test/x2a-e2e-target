# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing caching services, a FastAPI application, and an nginx multi-site reverse proxy with security hardening. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external cookbook dependencies, and migrating configuration data from Chef attributes to Ansible variables. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

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
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, and SSH configuration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration with self-signed certificates, fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration - contains node attributes, run list, and site-specific configuration data
- `solo.rb`: Chef Solo configuration file - defines cookbook paths and cache settings
- `Vagrantfile`: Development environment provisioning - likely contains VM configuration for testing
- `vagrant-provision.sh`: Shell provisioning script - bootstrap script for Vagrant environment setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible-community nginx role or custom nginx configuration tasks
- **memcached (~> 6.0)**: Replace with community.general.memcached module or custom package installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom Redis configuration management

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH hardening**: Root login disabled, password authentication disabled - preserve these security configurations in Ansible
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to ansible.posix.ufw module
- **Fail2ban configuration**: Intrusion prevention via template - migrate to community.general.fail2ban role
- **Sysctl security tuning**: Kernel parameter hardening via template - migrate to ansible.posix.sysctl module
- **Credential types per module**:
  - cache: Redis authentication password (hardcoded)
  - fastapi-tutorial: PostgreSQL database credentials (hardcoded)
  - nginx-multisite: SSL certificate generation (self-signed, no stored credentials)

### Technical Challenges

- **Redis configuration patching**: The cache cookbook uses a Ruby block to manually edit Redis configuration files post-installation - this hack needs to be replaced with proper template-based configuration in Ansible
- **Multi-site SSL management**: Dynamic SSL certificate generation for multiple sites requires careful loop handling in Ansible with proper certificate validation
- **Service dependency management**: PostgreSQL must be running before FastAPI application starts - ensure proper Ansible task ordering and handlers
- **Chef attribute override complexity**: The solo.json overrides default attributes from cookbooks - migrate this hierarchy to Ansible group_vars and host_vars structure

### Migration Order

1. **cache** (low risk, standalone service) - Independent caching services with clear external dependencies
2. **nginx-multisite** (moderate complexity) - Web server foundation needed for application deployment, security hardening can be validated independently
3. **fastapi-tutorial** (high complexity, dependencies) - Application deployment depends on database setup and potentially nginx for reverse proxy

### Assumptions

- The Vagrantfile and vagrant-provision.sh are used only for development/testing and may not need migration to production Ansible playbooks
- The "cluster.local" domain names suggest this is designed for internal/development use rather than public internet deployment
- SSL certificates are currently self-signed for development - production deployment may require integration with proper CA or Let's Encrypt
- The Redis configuration "hack" in the cache cookbook suggests compatibility issues with the redisio cookbook version that may not exist with direct Ansible Redis management
- PostgreSQL configuration beyond basic database/user creation is handled elsewhere or uses defaults
- The nginx external cookbook dependency provides the base nginx installation and configuration structure
- UFW firewall rules are sufficient for the security requirements - no iptables or other firewall management needed
- The current Chef Solo deployment model suggests single-node deployments rather than multi-node orchestration