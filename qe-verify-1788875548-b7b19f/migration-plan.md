# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration for a multi-site nginx web server with caching services and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, managing external dependencies, and addressing security configurations including SSL certificates and firewall rules. Estimated timeline: 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **nginx-multisite**:
    - Description: Nginx web server with multi-site SSL configuration, security hardening (fail2ban, UFW firewall), and self-signed certificate generation for development environments
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: SSL-enabled virtual hosts for test.cluster.local, ci.cluster.local, and status.cluster.local; fail2ban intrusion prevention; UFW firewall with SSH/HTTP/HTTPS rules; SSH hardening (root login disabled, password auth disabled); sysctl security tuning; custom lineinfile resource for configuration management

- **cache**:
    - Description: Caching layer services providing both in-memory (memcached) and persistent (Redis) caching with authentication and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service via external cookbook dependency; Redis 6379 with password authentication (redis_secure_password_123); custom configuration cleanup for Redis replica settings; log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning from https://github.com/dibanez/fastapi_tutorial.git; Python 3 virtual environment with pip dependencies; PostgreSQL database and user creation (fastapi/fastapi_password); systemd service management; environment configuration via .env file

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo run list configuration and node attributes including nginx site definitions, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration specifying cookbook paths, cache location, and logging settings
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider, network configuration (192.168.121.10), and port forwarding (80→8080, 443→8443)
- `vagrant-provision.sh`: Automated provisioning script for Chef installation, Berkshelf dependency resolution, and cookbook execution

### Target Details

- **Operating System**: Based on cookbook metadata supporting Ubuntu >= 18.04 and CentOS >= 7.0, with Vagrant using Fedora 42. Target recommendation: Red Hat Enterprise Linux 9 for production consistency.
- **Virtual Machine Technology**: Vagrant configuration specifies libvirt provider with 2GB RAM and 2 CPUs for development environment.
- **Cloud Platform**: Not specified - appears to be designed for on-premises or generic cloud deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx installation and configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached module or direct package installation with service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or manual Redis installation with custom configuration management
- **Chef Solo runtime**: Replace with Ansible playbook execution using ansible-playbook command
- **Berkshelf dependency management**: Replace with Ansible Galaxy requirements.yml for external role dependencies

### Security Considerations

- **SSL Certificate Management**: Current implementation uses self-signed certificates generated via OpenSSL commands. Migration approach: Implement ansible.builtin.openssl_certificate and ansible.builtin.openssl_privatekey modules for certificate generation, or integrate with Let's Encrypt using community.crypto collection
- **Firewall Configuration**: UFW rules managed through shell commands. Migration approach: Use community.general.ufw module for declarative firewall management
- **SSH Hardening**: Configuration changes via sed commands. Migration approach: Use ansible.builtin.lineinfile module for SSH configuration management
- **Fail2ban Configuration**: Template-based jail configuration. Migration approach: Use community.general.fail2ban module or template management with ansible.builtin.template
- **Vault/secrets management**: 
  - **nginx-multisite**: No encrypted secrets detected, SSL certificates are self-signed and generated dynamically
  - **cache**: 1 hardcoded credential detected - Redis password 'redis_secure_password_123' in recipes/default.rb
  - **fastapi-tutorial**: 2 hardcoded credentials detected - PostgreSQL user password 'fastapi_password' and database connection string in .env file
  - **Total credentials requiring vault management**: 3 credentials across 2 modules

### Technical Challenges

- **Custom Chef Resource Migration**: The nginx-multisite cookbook includes a custom 'lineinfile' resource (cookbooks/nginx-multisite/resources/lineinfile.rb) that provides file line management functionality. Migration approach: Replace with ansible.builtin.lineinfile module which provides equivalent functionality
- **Redis Configuration Cleanup**: The cache cookbook includes a Ruby block that performs regex-based configuration file cleanup to remove problematic Redis replica settings. Migration approach: Use ansible.builtin.replace module with regex patterns or ansible.builtin.template with conditional logic
- **Multi-site SSL Certificate Generation**: Dynamic certificate generation for multiple sites based on node attributes. Migration approach: Use ansible.builtin.loop with community.crypto.x509_certificate module for each site
- **Database Initialization**: PostgreSQL database and user creation using shell commands with error handling. Migration approach: Use community.postgresql.postgresql_db and community.postgresql.postgresql_user modules for idempotent database management
- **Systemd Service Template**: Inline service file creation within recipe. Migration approach: Use ansible.builtin.template module with separate service file template
- **Berkshelf Vendor Process**: Chef dependency resolution and vendoring. Migration approach: Implement Ansible Galaxy role installation in CI/CD pipeline or use ansible-galaxy install command

### Migration Order

1. **cache** (Priority 1 - low risk, standalone services)
   - Simple service installation and configuration
   - Limited external dependencies
   - Clear separation of concerns

2. **fastapi-tutorial** (Priority 2 - moderate complexity)
   - Application deployment with database dependencies
   - Git repository management and Python virtual environments
   - Systemd service configuration

3. **nginx-multisite** (Priority 3 - high complexity, multiple dependencies)
   - Complex multi-site configuration with SSL
   - Security hardening across multiple services
   - Custom resource functionality requiring careful translation
   - Dependencies on completion of other services for full integration testing

### Assumptions

- **Target Environment**: Assuming migration to Red Hat Enterprise Linux 9 based on enterprise patterns, though cookbooks support Ubuntu/CentOS. Confirmation needed for actual target OS.
- **SSL Certificate Strategy**: Current self-signed certificates are suitable for development. Production deployment may require integration with organizational PKI or Let's Encrypt. Clarification needed on production certificate management requirements.
- **Database Persistence**: FastAPI application assumes local PostgreSQL installation. Production deployment may require external database service integration. Confirmation needed on database architecture.
- **Network Configuration**: Vagrant configuration uses private networking (192.168.121.10) for development. Production network configuration and DNS management strategy needs clarification.
- **Secrets Management**: Hardcoded passwords in Chef recipes suggest development environment. Production deployment requires integration with organizational secrets management system (HashiCorp Vault, Azure Key Vault, etc.).
- **Service Discovery**: Multi-site configuration uses static hostnames (*.cluster.local). Production deployment may require dynamic service discovery or load balancer integration.
- **Backup and Recovery**: No backup strategies identified in current Chef configuration. Production Ansible implementation may need backup automation for databases and SSL certificates.
- **Monitoring and Logging**: Current implementation lacks monitoring integration. Production migration may require observability stack integration (Prometheus, ELK, etc.).
- **High Availability**: Single-node deployment pattern identified. Production requirements for load balancing, clustering, and failover need clarification.
- **Compliance Requirements**: Security hardening suggests compliance needs, but specific standards (SOC2, PCI-DSS, etc.) not identified. Compliance framework requirements need clarification for Ansible implementation.