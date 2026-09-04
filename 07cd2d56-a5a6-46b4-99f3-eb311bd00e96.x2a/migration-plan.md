# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 7 custom modules implementing a multi-tier web application stack. The migration involves converting Puppet manifests, ERB/EPP templates, custom Ruby functions, and Hiera data to Ansible playbooks, Jinja2 templates, and variable structures. Estimated timeline: 6-8 weeks for a team of 2-3 engineers with moderate Puppet and Ansible experience.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, and system utilities with MOTD management and package installation
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: MOTD template management, utility package installation, custom defined types for configuration entries and directory creation

**profile**:
- Description: Profile orchestration module containing base system configuration, application stack wrapper, cache management, and load balancer profiles
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Base OS configuration (NTP, syslog, utilities), application stack delegation, modular profile architecture

**profile_app_stack**:
- Description: Complete Python web application stack with PostgreSQL database, systemd service management, and monitoring integration
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, Gunicorn WSGI server, systemd service hardening, log rotation, custom Ruby function for database URL construction

**profile_haproxy**:
- Description: HAProxy load balancer with SSL termination, backend discovery, firewall integration, and statistics dashboard
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: Dynamic backend configuration, SSL/TLS support, statistics interface, firewall rule management, service discovery integration, ERB template-based configuration

**profile_postgresql**:
- Description: PostgreSQL database server installation and configuration with repository management and service control
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: PostgreSQL 15 installation, repository configuration, service management, basic database setup

**profile_redis_cluster**:
- Description: Redis cluster configuration with memory management and authentication
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: Redis installation, cluster configuration, memory limits, password authentication, template-based configuration

**puppetdb_query_stub**:
- Description: PuppetDB query stub library providing mock functions for testing environments
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Ruby library functions for PuppetDB query simulation

**role**:
- Description: Role definitions orchestrating multiple profiles for complete server configurations
- Path: site-modules/role
- Technology: Puppet
- Key Features: App server role combining base, HAProxy, application stack, and Redis cache profiles

### Infrastructure Files

- `Puppetfile`: Forge module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, inifile, and apt modules
- `environment.conf`: Module path configuration defining site-modules and modules directories
- `hiera.yaml`: 5-level Hiera hierarchy with per-node, OS family, environment, and common data layers
- `manifests/site.pp`: Site manifest with test Git repository setup and node classification
- `data/common.yaml`: Common Hiera data with application configuration, database credentials, and service parameters
- `data/environment/production.yaml`: Production environment overrides for NTP and syslog servers
- `data/environment/staging.yaml`: Staging environment configuration
- `Vagrantfile`: Local development environment configuration
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, Debian 11/12 (based on metadata.json operatingsystem_support)
- **Virtual Machine Technology**: Not specified in repository
- **Cloud Platform**: Not specified in repository

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with Ansible community.general collection and custom filters
- **puppetlabs-concat (9.0.2)**: Replace with Ansible template assembly or blockinfile module
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis configuration
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd and ansible.builtin.service modules
- **puppetlabs-inifile (6.1.1)**: Replace with community.general.ini_file module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository modules

### Security Considerations

- **Hardcoded credentials in Hiera data**: Multiple plaintext passwords found in data/common.yaml:
  - HAProxy stats password: "test-haproxy-password"
  - Database password: "test-db-password"  
  - Redis password: "test-redis-password"
  - Application secret key: "test-secret-key"
- **Systemd service hardening**: profile_app_stack implements security measures (NoNewPrivileges, ProtectSystem, ProtectHome, PrivateTmp) that need equivalent Ansible systemd unit configuration
- **SSL/TLS configuration**: HAProxy SSL settings and certificate management require Ansible certificate modules and secure file handling
- **File permissions**: Multiple modules manage file ownership and permissions that need careful translation to Ansible file module parameters
- **Vault/secrets management**: 4 credential instances detected across modules requiring Ansible Vault integration or external secret management

### Technical Challenges

- **Custom Ruby function migration**: profile_app_stack::app_db_url function needs conversion to Ansible Jinja2 filter or custom module for PostgreSQL URL construction with password encoding
- **Complex template logic**: HAProxy ERB template with conditional SSL blocks and backend iteration requires careful Jinja2 conversion
- **Hiera hierarchy translation**: 5-level hierarchy (node, OS family, environment, common) needs mapping to Ansible group_vars and host_vars structure
- **Puppet resource ordering**: Strict dependency chains (Class['profile_app_stack::python'] -> Class['profile_app_stack::database'] -> Class['profile_app_stack::app']) require Ansible handler and dependency management
- **Systemd service management**: Complex systemd unit template with security hardening needs equivalent Ansible systemd module configuration
- **Git repository deployment**: VCS repo management with revision control requires Ansible git module with proper change detection
- **Service discovery integration**: HAProxy discovery feature may need custom Ansible modules or external service discovery integration

### Migration Order

1. **base_utils** (low risk, foundational): Simple package management and MOTD configuration with minimal dependencies
2. **profile::base::base** (low risk, foundational): Basic OS services (NTP, syslog) with standard Ansible modules
3. **profile_postgresql** (moderate complexity): Database installation with repository management, prerequisite for application stack
4. **profile_redis_cluster** (moderate complexity): Cache layer configuration, independent of other services
5. **profile_app_stack** (high complexity): Complex application deployment with custom functions, Git integration, and systemd hardening
6. **profile_haproxy** (high complexity): Load balancer with SSL, discovery, and dynamic backend configuration
7. **role definitions** (integration): Final orchestration combining all profiles with proper dependency management

### Assumptions

- Test environment credentials are acceptable for initial migration and will be replaced with proper secret management
- Target systems have systemd for service management (indicated by systemd module dependency)
- Git repositories are accessible from target systems for application deployment
- PostgreSQL and Redis external dependencies are available via package managers
- HAProxy backend discovery feature may require additional service discovery infrastructure not present in current Puppet code
- SSL certificates referenced in HAProxy configuration exist and are managed externally
- Network firewall rules are managed at the OS level rather than external firewall appliances
- Python virtual environment creation follows standard patterns compatible with Ansible pip module
- Database initialization and schema management are handled by application code rather than Puppet/Ansible
- Log rotation configuration follows standard logrotate patterns
- Monitoring integration mentioned in profile_app_stack requires external monitoring system configuration
- Environment-specific overrides in Hiera will translate to Ansible inventory group variables
- Custom defined types in base_utils can be replaced with standard Ansible modules and tasks