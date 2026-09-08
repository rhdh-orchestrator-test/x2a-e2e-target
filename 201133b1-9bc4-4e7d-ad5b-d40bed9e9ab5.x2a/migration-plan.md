# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 8 custom modules implementing a multi-tier application stack architecture. The migration involves converting Puppet profiles, roles, and Hiera data to Ansible playbooks, roles, and variables. Estimated timeline: 6-8 weeks for a team of 2-3 engineers, with moderate complexity due to PuppetDB queries, custom functions, and multi-level Hiera hierarchy.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with custom Puppet functions and Bolt tasks
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: MOTD template management, utility package arrays, custom functions (ensure_value, normalize_port), Bolt health check tasks, platform info facts

**profile_app_stack**:
- Description: Full application stack orchestrator with Python application deployment, PostgreSQL database integration, systemd service management, and monitoring
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment via vcsrepo, custom database URL function, environment file templating, logrotate configuration, strict dependency chains

**profile_haproxy**:
- Description: HAProxy load balancer with multi-backend support, SSL termination, stats interface, firewall integration, and optional PuppetDB service discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: Dynamic backend configuration, SSL/TLS support, stats authentication, firewall rules, custom error pages, PuppetDB node discovery

**profile_postgresql**:
- Description: PostgreSQL database server installation with PGDG repository management and version pinning
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: PGDG repository setup, version-specific package installation, service management

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB-based node discovery and memory management policies
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB queries for cluster node discovery, memory policy configuration, cluster-aware setup

**puppetdb_query_stub**:
- Description: PuppetDB query function stub for testing and development environments
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Mock PuppetDB query functionality for non-production environments

**profile**:
- Description: Thin wrapper profiles that delegate to specific profile modules, implementing the roles/profiles pattern
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Base OS profile with NTP/syslog management, application stack wrapper, HAProxy wrapper

**role**:
- Description: Role definitions composing multiple profiles for complete node configurations
- Path: site-modules/role
- Technology: Puppet
- Key Features: Application server role, HAProxy load balancer role, Redis cluster role with Linux-specific exec paths

### Infrastructure Files

- `Puppetfile`: Forge module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, and apt modules
- `environment.conf`: Module path configuration defining site-modules precedence over Forge modules
- `hiera.yaml`: 4-level hierarchy (node-specific, OS family, environment, common) for configuration data
- `data/`: Hiera data directory with environment-specific and common configuration values
- `manifests/site.pp`: Main site manifest (entry point for node classification)
- `Vagrantfile`: Development environment configuration for testing
- `test/`: Container-based testing infrastructure

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, and Debian 11/12 based on metadata.json operatingsystem_support declarations
- **Virtual Machine Technology**: Not specified in Puppet configurations, but Vagrant development environment suggests VirtualBox/VMware compatibility
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic with potential for cloud deployment

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with Ansible community.general collection and custom filters
- **puppetlabs-concat (9.0.2)**: Replace with Ansible template and assemble modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis role
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository

### Security Considerations

- **Hiera encrypted data**: Database passwords, Redis passwords, HAProxy stats passwords, and application secret keys are stored in plain text in Hiera YAML files - migrate to Ansible Vault
- **SSL/TLS certificates**: HAProxy SSL certificate and key paths referenced in configuration - implement secure certificate deployment with Ansible Vault
- **Service authentication**: Multiple service-to-service authentication credentials need secure handling during migration
- **PuppetDB queries**: Replace with Ansible inventory plugins or dynamic inventory scripts for service discovery
- **File permissions**: Ensure proper ownership and permissions are maintained for application directories, configuration files, and log directories

### Technical Challenges

- **PuppetDB service discovery**: profile_redis_cluster and profile_haproxy use PuppetDB queries for dynamic node discovery - replace with Ansible inventory plugins, consul integration, or static inventory management
- **Custom Puppet functions**: profile_app_stack::app_db_url function builds database connection strings - convert to Jinja2 templates or Ansible filters
- **Hiera hierarchy complexity**: 4-level hierarchy (node, OS, environment, common) with deep merge - implement equivalent variable precedence in Ansible group_vars and host_vars
- **Strict dependency chains**: profile_app_stack enforces strict ordering with -> and ~> operators - replicate with Ansible handlers and task dependencies
- **Template engine differences**: ERB and EPP templates need conversion to Jinja2 with syntax adjustments for variable interpolation
- **Bolt task integration**: base_utils includes Bolt tasks for health checks - convert to Ansible ad-hoc commands or playbook tasks

### Migration Order

1. **base_utils** (low risk, foundational) - Common utilities and MOTD management with minimal dependencies
2. **profile_postgresql** (moderate complexity) - Database foundation required by application stack
3. **profile** (low risk) - Simple wrapper classes with straightforward conversion
4. **role** (low risk) - Role definitions that compose profiles
5. **profile_app_stack** (high complexity) - Complex application deployment with custom functions and strict dependencies
6. **profile_haproxy** (high complexity) - Load balancer with SSL, firewall integration, and service discovery
7. **profile_redis_cluster** (highest complexity) - Requires PuppetDB replacement and cluster coordination
8. **puppetdb_query_stub** (final phase) - Testing utility, migrate after main functionality is complete

### Assumptions

- Target environments will maintain the same OS support matrix (RHEL 8/9, Ubuntu 22.04/24.04, Debian 11/12)
- Ansible control node has network access to all managed nodes for SSH-based management
- Current Hiera data values represent production-ready configurations that can be migrated as-is to Ansible variables
- PuppetDB functionality can be replaced with Ansible inventory plugins or external service discovery mechanisms
- SSL certificates referenced in HAProxy configuration are available and can be deployed via Ansible Vault
- Application repositories referenced in profile_app_stack are accessible from Ansible control node
- PostgreSQL PGDG repositories will remain the preferred installation method for database components
- Systemd service management patterns can be directly translated to Ansible systemd module calls
- Firewall management requirements can be satisfied with standard Ansible firewall modules
- Development and testing workflows using Vagrant can be adapted to molecule or similar Ansible testing frameworks