# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a sophisticated Puppet control repository with 7 custom modules implementing a complete application stack infrastructure. The migration involves converting role-based profiles, complex Hiera hierarchies, and PuppetDB-based service discovery to Ansible equivalents. Estimated timeline: 8-12 weeks for a team of 2-3 engineers, with 2-3 weeks for planning, 4-6 weeks for core migration, and 2-3 weeks for testing and validation.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with cross-platform support
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: ERB template for MOTD, Hiera-driven package lists, custom Puppet functions (ensure_value, normalize_port), Bolt tasks for health checks

**profile_app_stack**:
- Description: Complete Python application stack with PostgreSQL database, systemd service management, and strict dependency orchestration
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment, Python virtual environment setup, Gunicorn WSGI server, database URL generation via custom function, EPP systemd templates, logrotate configuration

**profile_haproxy**:
- Description: HAProxy load balancer with multi-backend support, SSL termination, stats interface, and optional PuppetDB-based backend discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: ERB configuration templates, firewall rule management, custom error pages, 21-level Hiera hierarchy, PuppetDB query integration for dynamic backend discovery

**profile_postgresql**:
- Description: PostgreSQL installation with PGDG repository management and version pinning for Debian/Ubuntu systems
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: APT repository configuration, package version control, service management

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB-based node discovery and memory management policies
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB query for cluster member discovery, memory policy configuration, custom Facter facts for Redis role detection

**role**:
- Description: Role composition module defining server types through profile inclusion (app_server role includes base, haproxy, app stack, and redis profiles)
- Path: site-modules/role
- Technology: Puppet
- Key Features: Role-based server classification, profile orchestration

**profile**:
- Description: Profile wrapper module providing simplified class names for role composition
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Namespace organization for profile classes

**puppetdb_query_stub**:
- Description: PuppetDB query function stub for testing environments without PuppetDB connectivity
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Mock PuppetDB query responses for development/testing

### Infrastructure Files

- `Puppetfile`: Forge module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, inifile, and apt modules
- `environment.conf`: Module path configuration defining site-modules as primary module source
- `hiera.yaml`: 5-level hierarchy with per-node, per-OS, per-environment, and common data layers
- `manifests/site.pp`: Node classification with test Git repository setup and role assignment
- `data/common.yaml`: Environment-wide Hiera data with application configuration, database credentials, and service parameters
- `Vagrantfile`: Local development environment configuration
- `test/`: Container-based testing infrastructure with Containerfile and test runner

### Target Details

- **Operating System**: Red Hat Enterprise Linux 9 and Ubuntu 24.04 LTS (based on metadata.json operatingsystem_support across modules)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin and community.general modules for common utilities
- **puppetlabs-concat (9.0.2)**: Replace with Ansible template module and file assembly techniques
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw modules
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module for repository management
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis configuration tasks
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-inifile (6.1.1)**: Replace with community.general.ini_file module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository modules

### Security Considerations

- **Hiera encrypted data**: Multiple hardcoded passwords visible in common.yaml including database passwords, Redis passwords, HAProxy stats passwords, and application secret keys - requires migration to Ansible Vault
- **SSL/TLS certificates**: HAProxy SSL configuration references certificate paths that need secure deployment via Ansible Vault or external certificate management
- **Service credentials**: Database connection strings and authentication tokens embedded in configuration templates require vault encryption
- **PuppetDB queries**: Service discovery mechanism needs replacement with Ansible inventory or dynamic inventory scripts
- **File permissions**: Systemd service templates include security hardening (NoNewPrivileges, ProtectSystem) that must be preserved in Ansible service configurations

### Technical Challenges

- **PuppetDB service discovery**: profile_redis_cluster uses PuppetDB queries for cluster member discovery - requires replacement with Ansible inventory groups or dynamic inventory
- **Complex Hiera hierarchy**: 21-level hierarchy in HAProxy module needs flattening into Ansible group_vars and host_vars structure
- **Custom Puppet functions**: profile_app_stack::app_db_url function for database URL construction needs conversion to Jinja2 template or Ansible filter
- **Strict dependency chains**: profile_app_stack enforces strict ordering (python -> database -> app -> service -> monitoring) requiring careful Ansible handler and dependency management
- **ERB/EPP templates**: Multiple complex templates (haproxy.cfg.erb, app.service.epp) need conversion to Jinja2 with equivalent logic
- **Cross-module dependencies**: Role composition pattern requires careful Ansible playbook and role structure design

### Migration Order

1. **base_utils** (low risk, foundational): Simple utility module with minimal dependencies, provides foundation for other modules
2. **profile_postgresql** (moderate complexity): Database layer required by application stack, straightforward APT repository and package management
3. **profile_app_stack** (high complexity): Core application deployment with complex templating and dependency chains, requires base_utils and PostgreSQL
4. **profile_haproxy** (high complexity): Load balancer with advanced configuration and potential PuppetDB dependencies
5. **profile_redis_cluster** (highest complexity): Requires PuppetDB replacement strategy and cluster coordination logic
6. **role and profile wrappers** (low complexity): Simple composition modules, migrate after all profiles are complete

### Assumptions

- PuppetDB service discovery can be replaced with static Ansible inventory or dynamic inventory scripts
- Current hardcoded passwords in Hiera data are acceptable for development/testing environments and will be properly vaulted for production
- The 21-level Hiera hierarchy can be simplified to standard Ansible group_vars/host_vars structure without loss of functionality
- Custom Puppet functions can be replaced with equivalent Jinja2 templates or Ansible filters
- Systemd service management complexity can be preserved using Ansible's systemd module and template capabilities
- The strict dependency ordering in profile_app_stack can be maintained using Ansible handlers and task dependencies
- Container-based testing infrastructure can be adapted to use Ansible testing frameworks like Molecule
- Git repository deployment pattern using file:// URLs suggests local development environment that may need adjustment for production deployment workflows