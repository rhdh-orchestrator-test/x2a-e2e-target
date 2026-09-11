# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with SSL and security hardening. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and maintaining the existing security posture. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, and SSH configuration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL certificates (self-signed), fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configuration and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning (requires assessment for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible-community nginx role or custom nginx configuration tasks
- **memcached (~> 6.0)**: Replace with community.general.memcached module and package installation tasks
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom Redis configuration management
- **Chef Solo execution model**: Replace with Ansible playbook execution targeting localhost or remote hosts

### Security Considerations

- **Hardcoded credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi_password) are embedded in recipes and need migration to Ansible Vault
- **SSL certificate management**: Self-signed certificate generation needs conversion to Ansible crypto modules or integration with Let's Encrypt via certbot
- **SSH hardening**: Root login disable and password authentication disable configurations need migration to Ansible ssh_config management
- **Firewall rules**: UFW firewall configuration needs migration to community.general.ufw module
- **Fail2ban configuration**: Intrusion prevention settings need migration to Ansible fail2ban role or custom tasks
- **Sysctl security tuning**: Kernel parameter hardening needs migration to ansible.posix.sysctl module
- **Credential types per module**:
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables
  - nginx-multisite: SSL certificate generation, no external credential dependencies

### Technical Challenges

- **Redis configuration patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this complex logic needs careful conversion to Ansible lineinfile or template tasks
- **Multi-site SSL certificate generation**: The nginx-multisite cookbook dynamically generates SSL certificates for each configured site - requires Ansible loops and crypto module integration
- **Chef attribute inheritance**: The solo.json overrides default attributes from cookbooks - needs mapping to Ansible variable precedence and group_vars/host_vars structure
- **Service dependency management**: PostgreSQL must be running before FastAPI application starts - requires Ansible handler coordination and service dependency modeling
- **Cross-cookbook coordination**: The run list executes cookbooks in sequence - needs conversion to Ansible play ordering and role dependencies

### Migration Order

1. **cache** (low risk, standalone service): Memcached and Redis installation with basic configuration, test credential management patterns
2. **fastapi-tutorial** (moderate complexity): Python application deployment, database integration, systemd service management
3. **nginx-multisite** (high complexity, security dependencies): Multi-site configuration, SSL certificate management, security hardening integration

### Assumptions

- The target environment will maintain the same OS support matrix (Ubuntu 18.04+, CentOS 7+) unless explicitly changed
- Self-signed SSL certificates are acceptable for the target environment, or a migration to proper CA-signed certificates/Let's Encrypt will be handled separately
- The Vagrant development environment will be replaced with an equivalent Ansible-based local testing approach (ansible-playbook with localhost targeting)
- Database credentials and Redis passwords will be migrated to Ansible Vault rather than remaining as plaintext
- The current Chef Solo execution model (single-node, local execution) will be maintained in Ansible rather than migrating to a multi-node orchestration model
- UFW firewall rules are appropriate for the target environment and don't conflict with cloud provider security groups or other network security layers
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible and the main branch will continue to be the deployment target
- Systemd is available on target systems for service management (true for Ubuntu 18.04+ and CentOS 7+)
- The custom Redis configuration patching in the cache cookbook addresses specific version compatibility issues that may need different solutions in Ansible depending on the Redis version deployed