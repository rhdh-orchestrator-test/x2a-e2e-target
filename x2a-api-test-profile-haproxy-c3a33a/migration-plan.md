# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a sophisticated Puppet control repository with 8 custom modules implementing a multi-tier application stack architecture. The migration involves converting role-based profiles, complex Hiera hierarchies, and PuppetDB-based service discovery to Ansible equivalents. Estimated timeline: 8-12 weeks for a team of 2-3 engineers, with moderate complexity due to the layered profile architecture and cross-module dependencies.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with cross-platform support
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom Puppet functions (ensure_value, normalize_port), Bolt tasks for health checks, platform-specific Hiera data, custom facts via Ruby

**profile_app_stack**:
- Description: Full application stack orchestrator managing Python applications with PostgreSQL backend, systemd service management, and strict dependency chains
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Gunicorn WSGI server configuration, database URL generation via custom functions, systemd service hardening, log rotation, environment file management

**profile_haproxy**:
- Description: HAProxy load balancer profile with SSL termination, multi-backend support, stats interface, and firewall integration
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: 21-level Hiera hierarchy, SSL/TLS configuration, custom error pages, backend discovery via PuppetDB queries, firewall rule management

**profile_postgresql**:
- Description: PostgreSQL installation and configuration with PGDG repository management and version pinning
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: APT repository management, version-specific package installation, service lifecycle management

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB-based node discovery and memory management policies
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB queries for cluster member discovery, custom Redis configuration templates, memory policy management

**puppetdb_query_stub**:
- Description: PuppetDB query function stub providing compatibility layer for PuppetDB queries
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Ruby-based PuppetDB query function implementation

**profile**:
- Description: Thin wrapper profiles that delegate to specific implementation modules following role-profile-component pattern
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Base OS profile with NTP/syslog management, application stack wrapper, load balancer wrapper

**role**:
- Description: Role definitions composing multiple profiles for specific node types (app servers, load balancers, Redis clusters)
- Path: site-modules/role
- Technology: Puppet
- Key Features: Role-based node classification, profile composition with dependency ordering

### Infrastructure Files

- `Puppetfile`: Forge module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, inifile, and apt modules
- `environment.conf`: Module path configuration defining site-modules precedence over Forge modules
- `hiera.yaml`: 4-level hierarchy (per-node, per-OS, per-environment, common) with YAML data backend
- `data/common.yaml`: Environment-wide configuration defaults including credentials and service parameters
- `data/environment/`: Environment-specific overrides for production and staging
- `manifests/site.pp`: Main site manifest for node classification
- `Vagrantfile`: Local development environment configuration
- `test/`: Container-based testing infrastructure with Containerfile and test runner

### Target Details

- **Operating System**: Red Hat Enterprise Linux 9 and Ubuntu 24.04 LTS (based on metadata.json operatingsystem_support declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin and community.general collections
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.assemble or template concatenation
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis configuration
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository

### Security Considerations

- **Hiera Data Encryption**: Current setup uses plain YAML files with embedded credentials - migrate to Ansible Vault for sensitive data encryption
- **Database Credentials**: Multiple hardcoded passwords in data/common.yaml (test-db-password, test-haproxy-password, test-redis-password) require vault encryption
- **SSL Certificate Management**: HAProxy SSL configuration references certificate paths that need secure deployment via Ansible Vault
- **Service Account Secrets**: Application stack uses service account credentials that need proper secret management
- **SSH Key Management**: No visible SSH key management in current setup - may need addition for application deployment
- **Credential Types Per Module**:
  - profile_app_stack: Database passwords, application secret keys, repository credentials
  - profile_haproxy: Stats interface passwords, SSL certificate private keys
  - profile_redis_cluster: Redis authentication passwords
  - base_utils: No visible credentials

### Technical Challenges

- **PuppetDB Query Migration**: profile_redis_cluster uses PuppetDB queries for node discovery - replace with Ansible inventory groups or dynamic inventory scripts
- **Custom Puppet Functions**: base_utils contains custom Ruby functions (ensure_value, normalize_port) that need conversion to Ansible filters or custom modules
- **Complex Hiera Hierarchy**: 21-level hierarchy in profile_haproxy needs flattening to Ansible's group_vars/host_vars structure
- **Strict Dependency Ordering**: profile_app_stack enforces strict class dependency chains that need conversion to Ansible task dependencies and handlers
- **Cross-Module Communication**: Role-profile-component pattern needs restructuring to Ansible playbook and role architecture
- **Template Complexity**: ERB and EPP templates with complex logic need conversion to Jinja2 with equivalent functionality
- **Bolt Task Integration**: health_check.pp and rolling_restart.pp Bolt tasks need conversion to Ansible ad-hoc commands or playbooks

### Migration Order

1. **base_utils** (low risk, foundational): Common utilities and helper functions - establishes patterns for other modules
2. **profile_postgresql** (moderate complexity): Database layer with minimal dependencies - enables application stack testing
3. **profile_app_stack** (high complexity): Core application logic with database dependencies - central to the architecture
4. **profile_haproxy** (high complexity): Load balancer with backend discovery - depends on application stack for meaningful testing
5. **profile_redis_cluster** (highest complexity): Requires PuppetDB query replacement and cluster coordination logic
6. **profile and role modules** (integration phase): Wrapper classes that compose the individual profiles into complete node configurations

### Assumptions

- The repository represents a complete Puppet control repository with all necessary modules for a multi-tier web application
- Target environments support both Red Hat and Debian-based distributions as indicated in metadata.json files
- PuppetDB is currently used for service discovery and will need replacement with Ansible inventory or external service discovery
- The test infrastructure using containers suggests the application stack is containerizable, which may influence the Ansible migration approach
- Hiera data files contain test/development credentials that will need proper secret management in production
- The role-profile-component pattern indicates a mature Puppet codebase that follows best practices, suggesting the team has infrastructure-as-code experience
- Custom Ruby functions and facts indicate advanced Puppet usage that will require equivalent Ansible custom modules or filters
- The presence of Bolt tasks suggests the team uses Puppet for both configuration management and orchestration, requiring Ansible playbook equivalents
- SSL/TLS configuration in HAProxy suggests production-ready load balancing that needs careful migration to maintain security posture
- Systemd service management with security hardening indicates modern Linux target environments with systemd init system