# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 6 custom modules implementing a multi-tier web application stack. The migration involves converting role-based profiles, Hiera data hierarchy, and PuppetDB-based service discovery to Ansible equivalents. Estimated timeline: 6-8 weeks for a team of 2-3 engineers, with 2 weeks for planning, 4 weeks for module conversion, and 2 weeks for testing and validation.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with cross-platform support
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom Puppet functions (ensure_value, normalize_port), Bolt tasks for health checks, platform-specific Hiera data, MOTD template management

**profile_app_stack**:
- Description: Full application stack orchestrator for Python web applications with PostgreSQL backend, systemd service management, and strict dependency ordering
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment via vcsrepo, custom database URL function, environment file templating, logrotate configuration, monitoring integration

**profile_haproxy**:
- Description: HAProxy load balancer profile with SSL termination, multi-backend support, stats interface, and optional PuppetDB-based backend discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: 21-level Hiera hierarchy, dynamic backend configuration, firewall integration, SSL/TLS configuration, custom error pages

**profile_postgresql**:
- Description: PostgreSQL database server installation with PGDG repository management and version pinning
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: APT repository management, version-specific package installation, service management

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB-based node discovery and memory management policies
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB query integration, cluster node discovery, memory policy configuration, password authentication

**role**:
- Description: Role composition module defining server types (app_server, app_stack, haproxy, redis_cluster) with profile orchestration
- Path: site-modules/role
- Technology: Puppet
- Key Features: Role-based classification, profile composition, dependency ordering between base and application profiles

**profile**:
- Description: Thin wrapper profiles that delegate to specific profile modules for consistent interface
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Abstraction layer for profile_haproxy and profile_app_stack modules

**puppetdb_query_stub**:
- Description: PuppetDB query function stub for testing environments without PuppetDB connectivity
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Mock PuppetDB query function for development and testing

### Infrastructure Files

- `Puppetfile`: External module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, inifile, and apt modules
- `environment.conf`: Module path configuration defining site-modules as primary module source
- `hiera.yaml`: 4-level hierarchy (per-node, per-OS, per-environment, common) for configuration data
- `data/common.yaml`: Environment-wide configuration defaults including credentials and application settings
- `data/environment/*.yaml`: Environment-specific overrides for production and staging
- `manifests/site.pp`: Node classification and test application repository setup
- `Vagrantfile`: Local development environment configuration
- `test/`: Container-based testing infrastructure

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, Debian 11/12 based on module metadata operatingsystem_support
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin and community.general collections
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.template and ansible.builtin.assemble modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis configuration
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository modules

### Security Considerations

- **Hardcoded credentials in Hiera data**: Multiple plaintext passwords found in data/common.yaml including HAProxy stats password, database password, Redis password, and application secret key - migrate to Ansible Vault
- **SSL/TLS certificate management**: HAProxy SSL configuration with certificate and key paths - implement secure certificate deployment with Ansible Vault
- **SSH hardening configurations**: SSH client alive interval and root login restrictions defined in Hiera - migrate to ansible.posix.sshd_config module
- **Database credentials**: PostgreSQL connection strings with embedded passwords - secure with Ansible Vault and environment variables
- **Service authentication**: Redis password authentication and application secret keys - implement proper secrets management

### Technical Challenges

- **PuppetDB service discovery**: profile_redis_cluster uses PuppetDB queries for dynamic node discovery - replace with Ansible inventory groups or dynamic inventory plugins
- **Complex Hiera hierarchy**: 21-level hierarchy in profile_haproxy with per-node, cluster, datacenter, environment, and OS-specific data - redesign using Ansible group_vars and host_vars structure
- **Custom Puppet functions**: profile_app_stack::app_db_url function for database URL construction - reimplement as Jinja2 template or Ansible filter plugin
- **Strict dependency ordering**: profile_app_stack enforces strict class dependency chains - migrate to Ansible handlers and task dependencies
- **Cross-platform support**: Modules support RedHat, Debian, and Ubuntu with OS-specific configurations - implement using ansible.builtin.setup facts and when conditions
- **Template engine differences**: ERB and EPP templates need conversion to Jinja2 with different syntax for variables and conditionals

### Migration Order

1. **base_utils** (low risk, foundational): Utility functions, MOTD management, and package installation - provides foundation for other modules
2. **profile_postgresql** (moderate complexity): Database server setup with repository management - required dependency for application stack
3. **profile_redis_cluster** (high complexity): Redis configuration with PuppetDB dependency - complex service discovery migration
4. **profile_haproxy** (high complexity): Load balancer with complex Hiera hierarchy and SSL configuration - extensive configuration management
5. **profile_app_stack** (highest complexity): Full application deployment with Git integration, database connectivity, and service orchestration - most complex dependencies
6. **role and profile wrappers** (low risk): Role composition and profile delegation - simple orchestration layer

### Assumptions

- PuppetDB service discovery in profile_redis_cluster can be replaced with static Ansible inventory or dynamic inventory plugins
- The 21-level Hiera hierarchy in profile_haproxy can be flattened to Ansible's group_vars/host_vars structure without losing functionality
- Custom Puppet functions (ensure_value, normalize_port, app_db_url) can be reimplemented as Ansible filter plugins or Jinja2 templates
- Bolt tasks and plans in base_utils are used for operational tasks and may need separate migration to Ansible playbooks
- The test environment setup in site.pp is for development only and may not need migration to production Ansible
- SSL certificate files referenced in HAProxy configuration exist on target systems or will be deployed separately
- Database initialization and schema management handled by Alembic migrations will continue to work with Ansible-deployed applications
- The strict dependency ordering in profile_app_stack (python -> database -> app -> service -> monitoring) is critical for application functionality
- Environment-specific Hiera data (production.yaml, staging.yaml) contains sensitive overrides that will need Ansible Vault encryption
- The modular structure with separate install, config, and service classes can be consolidated into single Ansible roles without losing functionality