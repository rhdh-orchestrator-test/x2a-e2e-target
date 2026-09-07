# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration for a multi-site nginx web server with caching services and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external dependencies, and addressing security configurations including SSL certificates and system hardening. Estimated timeline: 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **nginx-multisite**:
    - Description: Nginx web server with multi-site SSL configuration, security hardening (fail2ban, UFW firewall), SSH hardening, and self-signed certificate generation for development environments
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: SSL-enabled virtual hosts for test.cluster.local, ci.cluster.local, and status.cluster.local; fail2ban intrusion prevention; UFW firewall with HTTP/HTTPS/SSH rules; SSH root login and password authentication disabled; sysctl security tuning; custom lineinfile resource for configuration management

- **cache**:
    - Description: Caching layer services providing both in-memory (memcached) and persistent (Redis) caching with authentication and custom configuration management
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service via external cookbook dependency; Redis 6379 with password authentication (redis_secure_password_123); custom Redis configuration cleanup to remove deprecated directives; log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python 3 virtual environment setup; Git repository cloning from https://github.com/dibanez/fastapi_tutorial.git; PostgreSQL database and user creation; systemd service configuration for uvicorn ASGI server on port 8000; environment variable configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo run list and node attributes defining nginx sites configuration, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration specifying cookbook paths and logging settings
- `Vagrantfile`: Development environment using Fedora 42 with libvirt provider, port forwarding (80→8080, 443→8443), and rsync folder synchronization
- `vagrant-provision.sh`: Automated provisioning script installing Chef, Berkshelf, downloading dependencies, and running Chef Solo

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on cookbook metadata.rb supports declarations). Default to Red Hat Enterprise Linux 9 for production deployment.
- **Virtual Machine Technology**: KVM/libvirt (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified - appears to be on-premises or private cloud deployment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **Chef Berkshelf**: Replace with Ansible Galaxy for role dependencies via requirements.yml
- **Chef Solo**: Replace with ansible-playbook execution

### Security Considerations
- **SSL Certificate Management**: Self-signed certificate generation using OpenSSL commands needs migration to community.crypto.openssl_* modules with proper certificate validation and renewal strategies
- **Firewall Configuration**: UFW firewall rules need migration to community.general.ufw module with equivalent port allowances (22/tcp, 80/tcp, 443/tcp)
- **SSH Hardening**: SSH configuration changes (PermitRootLogin no, PasswordAuthentication no) need migration to ansible.posix.sshd_config module
- **System Security**: Sysctl security parameters need migration to ansible.posix.sysctl module
- **Vault/secrets management**: 
  - **cache cookbook**: 1 hardcoded Redis password ('redis_secure_password_123') in recipes/default.rb - migrate to Ansible Vault
  - **fastapi-tutorial cookbook**: 1 hardcoded PostgreSQL password ('fastapi_password') in recipes/default.rb - migrate to Ansible Vault
  - **nginx-multisite cookbook**: SSL certificate paths and security configurations - consider Ansible Vault for sensitive paths
  - Total: 2 hardcoded credentials requiring Ansible Vault migration

### Technical Challenges
- **Custom Chef Resource Migration**: The lineinfile.rb custom resource in nginx-multisite needs migration to ansible.builtin.lineinfile module with equivalent functionality for file content management
- **Redis Configuration Cleanup**: The ruby_block "fix_redis_config" hack that removes deprecated Redis directives needs proper template-based configuration management in Ansible
- **Multi-site SSL Certificate Generation**: The dynamic SSL certificate generation loop for multiple sites needs careful migration to Ansible with proper certificate lifecycle management
- **Service Dependencies**: PostgreSQL service dependency for FastAPI application needs proper Ansible handler and dependency management
- **Git Repository Cloning**: FastAPI tutorial Git cloning with specific revision tracking needs migration to ansible.builtin.git module

### Migration Order
1. **cache cookbook** (low risk, minimal dependencies) - Start with caching services as they have clear external dependencies and straightforward configuration
2. **fastapi-tutorial cookbook** (moderate complexity) - Python application with database dependencies but well-defined service boundaries
3. **nginx-multisite cookbook** (high complexity, multiple dependencies) - Complex multi-site configuration with custom resources, security hardening, and SSL management

### Assumptions
- The target environment will maintain the same OS family (Ubuntu/CentOS) as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments; production may require Let's Encrypt or CA-signed certificates
- The FastAPI tutorial Git repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the 'main' branch is stable
- Redis password authentication is required in the target environment and the current password can be migrated to Ansible Vault
- PostgreSQL database will be co-located on the same server as the FastAPI application
- UFW firewall is the preferred firewall solution for the target Ubuntu environment
- The Vagrant development environment will be replaced with equivalent Ansible testing using molecule or similar testing frameworks
- Network configuration (192.168.121.10 IP, port forwarding) is specific to development and will be adapted for production environments
- The Chef Berkshelf vendoring process can be replaced with Ansible Galaxy role installation
- Systemd is available on the target systems for service management
- The current fail2ban configuration is sufficient and doesn't require advanced intrusion detection features