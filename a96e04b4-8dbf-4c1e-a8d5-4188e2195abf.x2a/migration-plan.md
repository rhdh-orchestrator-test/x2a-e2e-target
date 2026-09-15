# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 6 custom modules implementing a multi-tier web application stack. The migration involves converting Puppet manifests, Hiera data, and ERB templates to Ansible playbooks, roles, and Jinja2 templates. Estimated timeline: 6-8 weeks for a team of 2-3 engineers, with 2 weeks for testing and validation.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, and system utilities with MOTD management and package installation
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom Puppet functions (ensure_value, normalize_port), Bolt tasks for health checks, platform-specific Hiera data, MOTD template management

**profile_app_stack**:
- Description: Full application stack orchestrator for Python web applications with PostgreSQL database, systemd service management, and monitoring
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment via vcsrepo, custom database URL function, environment-specific configuration, logrotate integration, strict dependency chain enforcement

**profile_haproxy**:
- Description: HAProxy load balancer with SSL termination, multi-backend support, stats interface, and firewall integration
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: 21-level Hiera hierarchy, PuppetDB service discovery, SSL/TLS configuration, custom error pages, firewall rule management

**profile_postgresql**:
- Description: PostgreSQL database server installation with PGDG repository management and version pinning
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: APT repository configuration, version-specific package management, service lifecycle management

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB-based node discovery and memory management
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB query integration for cluster member discovery, memory policy configuration, password authentication

**profile**:
- Description: Thin wrapper profiles that delegate to specific implementation modules (app/stack, loadbalancer/haproxy)
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Environment-aware delegation pattern, fact-based configuration

**role**:
- Description: Role composition layer combining base profiles with specific service profiles (app_stack, haproxy, redis_cluster)
- Path: site-modules/role
- Technology: Puppet
- Key Features: Linux-specific path configuration, dependency ordering between base and service profiles

### Infrastructure Files

- `Puppetfile`: Forge module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, inifile, and apt modules
- `environment.conf`: Module path configuration defining site-modules precedence over Forge modules
- `hiera.yaml`: 4-level hierarchy (node → OS family → environment → common) for configuration data
- `data/`: Hierarchical configuration data with environment-specific overrides and OS-specific settings
- `manifests/site.pp`: Main site manifest (entry point for node classification)
- `Vagrantfile`: Local development environment configuration
- `test/`: Container-based testing infrastructure with Containerfile and test runner

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, Debian 11/12 (multi-OS support based on metadata.json specifications)
- **Virtual Machine Technology**: Not specified (inferred from Vagrant configuration suggesting VirtualBox/VMware compatibility)
- **Cloud Platform**: Not specified (no cloud-specific configurations detected)

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin and community.general collections
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.assemble or template concatenation
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis configuration
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt_repository and apt modules

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found in Hiera data (haproxy stats, database, Redis, application secret key) - migrate to Ansible Vault
- **SSL/TLS Configuration**: HAProxy SSL certificate and key paths configured but not encrypted - implement certificate management with Ansible Vault
- **SSH Hardening**: SSH configuration parameters in Hiera (permit_root_login: false, client_alive_interval) - migrate to ansible.builtin.lineinfile or openssh role
- **Database Credentials**: PostgreSQL connection strings with embedded passwords in templates - encrypt with Ansible Vault and use no_log directives
- **Application Secrets**: Secret keys and API tokens in environment templates - migrate to encrypted variables with proper secret rotation capabilities

### Technical Challenges

- **PuppetDB Integration**: profile_redis_cluster uses PuppetDB queries for node discovery - replace with Ansible inventory groups or dynamic inventory scripts
- **Custom Puppet Functions**: profile_app_stack::app_db_url function builds database URLs - reimplement as Jinja2 filters or Ansible lookup plugins
- **Hiera Hierarchy**: 21-level hierarchy in HAProxy module requires careful variable precedence mapping to Ansible group_vars/host_vars structure
- **Strict Dependency Chains**: Puppet's contain/require/notify relationships need conversion to Ansible handlers and task dependencies
- **ERB Template Logic**: Complex conditional logic in app.env.erb template requires Jinja2 conversion with environment-specific variable handling
- **Bolt Task Integration**: Health check and rolling restart tasks need conversion to Ansible playbooks or modules

### Migration Order

1. **base_utils** (low risk, foundational) - Utility functions and basic system configuration
2. **profile_postgresql** (moderate complexity) - Database layer with repository management
3. **profile_redis_cluster** (high complexity) - Requires PuppetDB replacement strategy
4. **profile_app_stack** (high complexity) - Complex orchestration with custom functions
5. **profile_haproxy** (highest complexity) - Advanced Hiera hierarchy and service discovery
6. **profile and role** (integration phase) - Wrapper classes and role composition

### Assumptions

- Target environments will use the same OS distributions specified in module metadata (RHEL 8/9, Ubuntu 22.04/24.04, Debian 11/12)
- PuppetDB functionality can be replaced with Ansible inventory or external service discovery mechanisms
- Current Hiera encryption (if any) uses eyaml or similar, requiring migration to Ansible Vault
- Git repositories referenced in vcsrepo resources are accessible from target Ansible control nodes
- HAProxy backend discovery can be migrated to static inventory or external service registry integration
- Bolt tasks are not critical path dependencies and can be replaced with equivalent Ansible ad-hoc commands or playbooks
- Current Puppet Server infrastructure will remain available during migration for reference and rollback scenarios
- SSL certificates referenced in HAProxy configuration are managed externally or can be integrated with Ansible certificate management workflows