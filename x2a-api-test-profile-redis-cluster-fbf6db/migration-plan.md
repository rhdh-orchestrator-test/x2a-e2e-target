# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a sophisticated Puppet control repository implementing a multi-tier application stack with load balancing, caching, and database components. The migration involves 8 distinct modules with complex interdependencies, Hiera-based configuration management, and PuppetDB integration. Estimated timeline: 8-12 weeks for a team of 2-3 engineers, with 2-3 weeks for testing and validation.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with custom Puppet functions and Bolt tasks
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom defined types, Puppet functions (ensure_value, normalize_port), Facter facts, Bolt tasks for health checks and rolling restarts

**profile_app_stack**:
- Description: Full application stack orchestrator managing Python application deployment with PostgreSQL database, systemd service, and monitoring in strict dependency chain
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository cloning via vcsrepo, Python virtualenv management, database migrations with Alembic, systemd service templates, custom Puppet function for database URL construction

**profile_haproxy**:
- Description: HAProxy load balancer profile with multi-backend support, SSL termination, stats interface, and PuppetDB-based service discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: Dynamic backend configuration, SSL/TLS with custom ciphers, stats authentication, firewall integration, service discovery via PuppetDB queries

**profile_postgresql**:
- Description: PostgreSQL installation with PGDG repository management and version pinning for Debian/Ubuntu systems
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: APT repository configuration, package version pinning, service management

**profile_redis_cluster**:
- Description: Redis cluster profile using puppet-redis module with PuppetDB node discovery for automatic cluster member detection
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB queries for node discovery, memory policy configuration, cluster-aware setup

**puppetdb_query_stub**:
- Description: PuppetDB query function stub providing compatibility layer for PuppetDB queries in testing environments
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Custom Puppet function for PuppetDB integration

**profile**:
- Description: Profile wrapper classes providing thin delegation layer between roles and implementation modules
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Base OS profile with NTP/syslog management, application stack wrapper, load balancer wrapper

**role**:
- Description: Role classes composing profiles into complete node configurations for application servers and load balancers
- Path: site-modules/role
- Technology: Puppet
- Key Features: Role-based node classification, profile composition with dependency ordering

### Infrastructure Files

- `Puppetfile`: External module dependencies from Puppet Forge - requires mapping to Ansible Galaxy/collections
- `environment.conf`: Module path configuration - needs translation to Ansible directory structure
- `hiera.yaml`: 4-level hierarchy (node → OS → environment → common) - requires Ansible variable precedence design
- `data/common.yaml`: Global configuration with hardcoded passwords - needs Ansible Vault migration
- `data/environment/*.yaml`: Environment-specific overrides - maps to Ansible group_vars
- `manifests/site.pp`: Node classification logic - requires Ansible inventory design
- `Vagrantfile`: Development environment - can be adapted for Ansible testing
- `test/`: Container-based testing - needs adaptation to molecule or similar

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Debian 11/12, Ubuntu 22.04/24.04 (multi-OS support based on metadata.json specifications)
- **Virtual Machine Technology**: Not specified (inferred from Vagrant configuration suggesting VirtualBox/VMware compatibility)
- **Cloud Platform**: Not specified (no cloud-specific configurations detected)

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin and community.general collections
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.template and ansible.builtin.assemble modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom tasks
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository modules

### Security Considerations

- **Hardcoded Passwords**: Multiple plaintext passwords in Hiera data files require Ansible Vault encryption:
  - HAProxy stats password: "test-haproxy-password"
  - Database password: "test-db-password" 
  - Redis password: "test-redis-password"
  - Application secret key: "test-secret-key"
- **SSL/TLS Configuration**: HAProxy SSL certificate paths and cipher configurations need secure variable management
- **Service Authentication**: Stats interfaces and database connections require credential rotation strategy
- **File Permissions**: Application .env files with mode 0600 contain sensitive environment variables

### Technical Challenges

- **PuppetDB Integration**: Redis cluster and HAProxy modules use PuppetDB queries for service discovery - requires Ansible dynamic inventory or fact caching solution
- **Custom Puppet Functions**: profile_app_stack::app_db_url function needs conversion to Jinja2 template or custom filter
- **Complex Dependency Chains**: Strict ordering in profile_app_stack (python → database → app → service → monitoring) requires careful Ansible handler and dependency design
- **Hiera Hierarchy**: 4-level data hierarchy with automatic parameter lookup needs variable precedence mapping in Ansible
- **Template Complexity**: ERB templates with conditional logic require Jinja2 conversion with equivalent conditionals
- **Facter Integration**: Custom facts (haproxy_version.rb, redis_role.rb) need conversion to Ansible custom facts or setup module extensions

### Migration Order

1. **base_utils** (low risk, foundational) - Common utilities and helper functions establish foundation
2. **profile_postgresql** (moderate complexity) - Database layer with minimal external dependencies  
3. **profile_redis_cluster** (high complexity) - Requires PuppetDB query replacement strategy
4. **profile_app_stack** (highest complexity) - Complex dependency chain and custom functions
5. **profile_haproxy** (high complexity) - Service discovery and SSL configuration dependencies
6. **profile + role** (integration phase) - Wrapper classes and node classification
7. **puppetdb_query_stub** (testing support) - Development/testing compatibility layer

### Assumptions

- Test environment passwords are placeholders and production uses proper secret management
- PuppetDB service discovery can be replaced with Ansible dynamic inventory or static configuration
- Current Vagrant-based development workflow can be adapted to molecule testing
- Multi-OS support requirements (RHEL/Debian/Ubuntu) will be maintained in Ansible version
- Existing backup scripts and health checks in profile_app_stack can be converted to Ansible modules
- HAProxy backend configuration complexity suggests production use of multiple application servers
- Git repository access for application deployment assumes SSH key or token-based authentication
- Python application follows standard structure with requirements.txt and Alembic migrations
- Database connection pooling and performance tuning are handled at application level, not in Puppet configuration
- Firewall management currently disabled ("firewall_provider: none") but infrastructure exists for future enablement