# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 6 custom modules implementing a multi-tier application stack. The migration involves converting Puppet profiles, roles, and Hiera data to Ansible playbooks, roles, and variables. Estimated timeline: 6-8 weeks for a team of 2-3 engineers, with moderate complexity due to PuppetDB queries, custom functions, and multi-level Hiera hierarchy.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with Bolt tasks for health checks
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom defined types, Puppet functions, Facter facts, MOTD template management, rolling restart plans

**profile_app_stack**:
- Description: Full application stack orchestrator with Python app deployment, PostgreSQL database setup, systemd service management, and monitoring integration
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment via vcsrepo, custom database URL function, environment file templating, logrotate configuration, strict dependency chain

**profile_haproxy**:
- Description: HAProxy load balancer profile with multi-backend support, SSL termination, stats interface, and optional PuppetDB-based service discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: Dynamic backend configuration, firewall integration, SSL/TLS support, stats authentication, custom error pages

**profile_postgresql**:
- Description: PostgreSQL installation with PGDG repository setup and version pinning for Debian/Ubuntu systems
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: APT repository management, package version control, service management

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB node discovery, memory management, and authentication
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB queries for cluster member discovery, memory policy configuration, password authentication

**puppetdb_query_stub**:
- Description: Stub implementation of PuppetDB query function for testing environments without PuppetDB
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Mock PuppetDB query responses, testing support

### Infrastructure Files

- `Puppetfile`: Forge module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, inifile, and apt modules
- `environment.conf`: Module path configuration defining site-modules as primary module location
- `hiera.yaml`: 4-level hierarchy (node → OS family → environment → common) requiring Ansible variable precedence mapping
- `data/common.yaml`: Global configuration defaults with hardcoded passwords and application settings
- `data/environment/*.yaml`: Environment-specific overrides for production and staging
- `manifests/site.pp`: Main site manifest (entry point for node classification)
- `Vagrantfile`: Development environment setup requiring conversion to Ansible testing framework
- `test/`: Container-based testing infrastructure needing migration to molecule or similar

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, Debian 11/12 based on module metadata operatingsystem_support
- **Virtual Machine Technology**: Not specified in configurations
- **Cloud Platform**: Not specified in configurations

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin collection and community.general modules
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.template and ansible.builtin.assemble modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis role
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository modules

### Security Considerations

- **Hardcoded passwords in Hiera data**: Multiple plaintext passwords found in data/common.yaml including database, Redis, and HAProxy stats credentials requiring migration to Ansible Vault
- **SSL/TLS certificate management**: HAProxy module references SSL certificate and key paths requiring secure certificate deployment strategy
- **Application secrets**: Secret key management in profile_app_stack requires Ansible Vault integration
- **SSH hardening configurations**: SSH client settings in common.yaml need migration to ansible.builtin.lineinfile or dedicated SSH role
- **Database credentials**: PostgreSQL user and password management requires secure credential handling
- **Service authentication**: HAProxy stats interface and Redis authentication need encrypted storage

### Technical Challenges

- **PuppetDB query dependency**: profile_redis_cluster uses PuppetDB queries for node discovery requiring replacement with Ansible inventory or dynamic inventory scripts
- **Custom Puppet functions**: profile_app_stack::app_db_url function needs conversion to Ansible Jinja2 template or custom filter
- **Complex Hiera hierarchy**: 4-level hierarchy (node → OS → environment → common) requires careful Ansible variable precedence mapping
- **Strict dependency chains**: profile_app_stack enforces strict ordering with containment and dependency arrows requiring Ansible handler and task ordering
- **Template engine differences**: ERB templates (.erb) and EPP templates (.epp) need conversion to Jinja2 syntax
- **Facter custom facts**: Custom facts in lib/facter/ directories require conversion to Ansible custom facts or setup module extensions
- **Bolt plans and tasks**: Operational tasks in plans/ and tasks/ directories need migration to Ansible playbooks or ad-hoc commands

### Migration Order

1. **base_utils** (low risk, foundational): Core utilities and helper functions used by other modules
2. **profile_postgresql** (moderate complexity): Database foundation required by application stack
3. **profile_app_stack** (high complexity): Complex orchestration with custom functions and strict dependencies
4. **profile_haproxy** (moderate complexity): Load balancer with dynamic configuration and SSL support
5. **profile_redis_cluster** (high complexity): PuppetDB dependency and cluster discovery logic
6. **puppetdb_query_stub** (low risk): Testing utility, can be replaced with Ansible testing framework

### Assumptions

- PuppetDB service discovery in profile_redis_cluster can be replaced with Ansible inventory-based discovery or eliminated in favor of static configuration
- Custom Puppet functions can be adequately replaced with Jinja2 templates and filters without loss of functionality
- The 4-level Hiera hierarchy can be mapped to Ansible's variable precedence system using group_vars, host_vars, and inventory structure
- Bolt plans and tasks are used for operational procedures that can be converted to Ansible playbooks or eliminated
- The testing framework in test/ directory uses containers and can be migrated to Molecule for Ansible role testing
- SSL certificates referenced in HAProxy configuration are managed externally and paths can be adapted for Ansible deployment
- The application deployment process using vcsrepo can be adequately replaced with ansible.builtin.git module
- Environment-specific configurations in data/environment/ can be mapped to Ansible inventory groups or environment-specific variable files
- Custom defined types in base_utils can be converted to Ansible tasks or custom modules without significant functionality loss