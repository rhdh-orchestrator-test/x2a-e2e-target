# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 8 custom modules implementing a multi-tier web application stack. The migration involves converting Puppet profiles and roles to Ansible roles, migrating Hiera data to Ansible variables, and replacing Puppet-specific features like PuppetDB queries and custom functions. Estimated timeline: 6-8 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, and Bolt tasks including MOTD management and utility package installation
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom defined types, Puppet functions, Facter facts, Bolt tasks for health checks and rolling restarts

**profile_app_stack**:
- Description: Full application stack orchestrator for Python applications with PostgreSQL backend, systemd service management, and strict dependency chains
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Gunicorn WSGI server configuration, database URL generation via custom functions, systemd unit templates, log rotation, security hardening

**profile_haproxy**:
- Description: HAProxy load balancer profile with multi-backend support, SSL termination, stats interface, and firewall integration
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: Dynamic backend discovery, SSL/TLS configuration, custom error pages, stats authentication, firewall rules

**profile_postgresql**:
- Description: PostgreSQL installation with PGDG repository management and version pinning
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: PGDG repository setup, version-specific package installation, service management

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB-based node discovery and memory management policies
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB queries for cluster member discovery, memory policy configuration, custom Facter facts

**puppetdb_query_stub**:
- Description: PuppetDB query function stub for testing environments without PuppetDB
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Mock PuppetDB query function for development/testing

**profile**:
- Description: Profile wrapper classes that compose individual profiles into logical groupings
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Profile composition for app stack, base configuration, cache layer, and load balancer

**role**:
- Description: Role classes that define complete node configurations by combining profiles
- Path: site-modules/role
- Technology: Puppet
- Key Features: Complete node role definitions for app servers, HAProxy load balancers, and Redis clusters

### Infrastructure Files

- `Puppetfile`: External module dependencies from Puppet Forge - needs conversion to Ansible Galaxy requirements
- `environment.conf`: Puppet environment configuration defining module search paths
- `hiera.yaml`: 4-level Hiera hierarchy (node → OS → environment → common) requiring conversion to Ansible variable precedence
- `data/`: Hiera data files with environment-specific and common configuration values
- `manifests/site.pp`: Main Puppet manifest entry point for node classification
- `Vagrantfile`: Development environment setup for testing
- `test/`: Container-based testing infrastructure

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, Debian 11/12 (based on metadata.json operatingsystem_support)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified in source configuration

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin and community.general modules
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.template and ansible.builtin.assemble
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis role
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd and ansible.builtin.template
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository

### Security Considerations

- **Hiera encrypted data**: Database passwords, Redis passwords, HAProxy stats passwords, and application secret keys are stored in plain text in Hiera data files - migrate to Ansible Vault
- **SSL/TLS certificates**: HAProxy SSL certificate and key paths referenced in configuration - implement secure certificate deployment with Ansible Vault
- **Service account credentials**: Application user credentials and database authentication - secure with Ansible Vault and proper file permissions
- **Systemd security hardening**: Profile_app_stack implements systemd security features (NoNewPrivileges, ProtectSystem, PrivateTmp) - preserve in Ansible systemd unit templates
- **SSH hardening**: SSH configuration parameters in Hiera data need migration to Ansible variables with proper security defaults

### Technical Challenges

- **PuppetDB queries**: profile_redis_cluster uses PuppetDB queries for dynamic node discovery - replace with Ansible inventory groups or dynamic inventory scripts
- **Custom Puppet functions**: profile_app_stack::app_db_url function for database URL generation - convert to Jinja2 templates or Ansible filters
- **Puppet dependency chains**: Strict ordering with -> and ~> operators throughout modules - implement with Ansible handlers and task dependencies
- **Hiera hierarchy**: 4-level hierarchy (node/OS/environment/common) - map to Ansible variable precedence using group_vars, host_vars, and role defaults
- **Facter custom facts**: Custom facts in base_utils and profile_redis_cluster - convert to Ansible custom facts or gather_facts extensions
- **Bolt tasks**: Health check and rolling restart tasks in base_utils - convert to Ansible playbooks or ad-hoc commands
- **ERB/EPP templates**: Complex templates with Ruby logic - convert to Jinja2 with equivalent functionality

### Migration Order

1. **base_utils** (low risk, foundational) - Common utilities and helper functions needed by other modules
2. **profile_postgresql** (moderate complexity) - Database layer with minimal dependencies
3. **profile_redis_cluster** (high complexity) - Requires PuppetDB query replacement and cluster logic
4. **profile_app_stack** (high complexity) - Complex application deployment with custom functions and strict dependencies
5. **profile_haproxy** (moderate complexity) - Load balancer with dynamic backend configuration
6. **profile and role** (low risk) - Wrapper classes that compose the migrated profiles

### Assumptions

- **Hiera data security**: Assuming all sensitive data in Hiera files (passwords, keys) will be migrated to Ansible Vault - current plain text storage is not production-ready
- **PuppetDB replacement**: Assuming Ansible dynamic inventory or static inventory groups can replace PuppetDB queries for node discovery in Redis clustering
- **Custom function complexity**: Assuming the profile_app_stack::app_db_url function performs simple string concatenation that can be replicated in Jinja2
- **Bolt task usage**: Assuming Bolt tasks are used for operational procedures that can be converted to Ansible playbooks
- **Template complexity**: Assuming ERB/EPP templates use standard Ruby constructs that have Jinja2 equivalents
- **Firewall provider**: HAProxy profile sets firewall_provider to "none" in test data - production firewall requirements need clarification
- **SSL certificate management**: HAProxy SSL configuration references certificate paths but certificate provisioning method is unclear
- **Database initialization**: PostgreSQL profile handles installation but database/user creation logic in app_stack module needs verification
- **Service discovery**: Redis cluster node discovery via PuppetDB may require architectural changes for Ansible implementation