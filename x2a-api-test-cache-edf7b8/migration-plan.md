# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration for a multi-site nginx web server with caching services and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external dependencies, and preserving security configurations. Estimated timeline: 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL-enabled multi-site configuration, security hardening via fail2ban/UFW, and self-signed certificate generation for development
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, sysctl security tuning, custom lineinfile resource

- **cache**:
    - Description: Caching layer with memcached and Redis services, including Redis authentication and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service via external cookbook, Redis 6379 with password authentication, custom Redis configuration cleanup, log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application with PostgreSQL database backend, systemd service management, and virtual environment setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning from GitHub, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook references
- `solo.json`: Chef node attributes defining nginx sites configuration, SSL paths, and security settings (fail2ban, UFW, SSH hardening)
- `solo.rb`: Chef Solo configuration with cookbook paths and logging settings
- `Vagrantfile`: Development environment using Fedora 42 with libvirt provider, port forwarding (80→8080, 443→8443), and rsync folder sync
- `vagrant-provision.sh`: Automated Chef installation and Berkshelf dependency management script

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on cookbook metadata.rb supports declarations). Default to Red Hat Enterprise Linux 9 for production deployment.
- **Virtual Machine Technology**: Libvirt/KVM (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified - appears to be on-premises or private cloud deployment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **PostgreSQL**: Replace with community.postgresql.* collection modules
- **Python/pip packages**: Replace with ansible.builtin.pip module
- **Git repository cloning**: Replace with ansible.builtin.git module
- **SSL certificate generation**: Replace with community.crypto.openssl_* modules

### Security Considerations
- **SSL/TLS certificate management**: Self-signed certificates generated via OpenSSL commands - migrate to community.crypto collection for proper certificate lifecycle management
- **Hardcoded credentials**: 
  - Redis password: 'redis_secure_password_123' in cache/recipes/default.rb
  - PostgreSQL credentials: 'fastapi_password' in fastapi-tutorial/recipes/default.rb
  - Database connection string in .env file with embedded credentials
  - Total: 3 hardcoded credential instances requiring Ansible Vault migration
- **SSH hardening configurations**: Root login disabled, password authentication disabled - preserve in Ansible with ansible.posix.sshd_config module
- **Firewall rules**: UFW configuration with HTTP/HTTPS/SSH ports - migrate to community.general.ufw module
- **Fail2ban intrusion prevention**: Template-based jail configuration - migrate to community.general.fail2ban module
- **Sysctl security tuning**: Custom kernel parameter hardening - migrate to ansible.posix.sysctl module

### Technical Challenges
- **Custom lineinfile resource**: The nginx-multisite cookbook includes a custom Chef resource (resources/lineinfile.rb) that provides file line manipulation functionality. This needs to be replaced with Ansible's ansible.builtin.lineinfile module, requiring careful testing to ensure equivalent behavior.
- **Redis configuration cleanup**: The cache cookbook contains a Ruby block that performs regex-based cleanup of Redis configuration files, removing specific directives. This complex logic needs to be reimplemented using Ansible's ansible.builtin.replace or ansible.builtin.lineinfile modules with multiple tasks.
- **Chef notification system**: Extensive use of Chef's notifies mechanism for service reloads (nginx, fail2ban, ssh, systemd) - requires careful handler mapping in Ansible to maintain proper service restart ordering.
- **Berkshelf dependency resolution**: External cookbook dependencies need manual analysis to identify which Ansible collections provide equivalent functionality.
- **Template variable scoping**: Chef ERB templates use node attributes and recipe variables - requires conversion to Jinja2 templates with proper variable passing from Ansible tasks.

### Migration Order
1. **fastapi-tutorial** (low risk, high value): Straightforward application deployment with well-defined dependencies and minimal custom logic
2. **cache** (moderate complexity): Redis and memcached services with some custom configuration manipulation requiring careful testing
3. **nginx-multisite** (high complexity, dependencies): Complex multi-site SSL configuration with custom resources, security hardening, and extensive template usage - should be migrated last due to dependencies on other services

### Assumptions
- **Operating system compatibility**: Chef cookbooks support both Ubuntu 18.04+ and CentOS 7+, but Ansible migration will target RHEL 9 unless specific OS requirements are identified during testing
- **Development environment**: Vagrant with libvirt provider is used for development - Ansible testing environment may need adjustment for different virtualization platforms
- **SSL certificate strategy**: Self-signed certificates are acceptable for development, but production deployment may require integration with proper CA or Let's Encrypt
- **Database persistence**: PostgreSQL data persistence and backup strategies are not defined in the current Chef configuration - may need to be addressed in Ansible migration
- **Service discovery**: The current configuration uses static hostnames (*.cluster.local) - unclear if dynamic service discovery is required in the target environment
- **Monitoring and logging**: No monitoring or centralized logging configuration is present in the Chef cookbooks - may need to be added during Ansible migration
- **High availability**: Single-node deployment assumed based on current configuration - clustering and load balancing requirements are not specified
- **Network security**: Current UFW configuration allows basic HTTP/HTTPS/SSH access - additional network security requirements (VPN, specific IP restrictions) are not defined
- **Backup and recovery**: No backup procedures are defined for databases, SSL certificates, or application data - disaster recovery strategy needs clarification
- **Performance tuning**: Nginx, Redis, and PostgreSQL use default configurations - production performance requirements and tuning parameters are not specified