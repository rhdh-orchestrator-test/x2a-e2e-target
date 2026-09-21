# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 7 custom modules implementing a multi-tier web application stack. The migration involves converting Puppet profiles, roles, and Hiera data to Ansible playbooks, roles, and variables. Estimated timeline: 6-8 weeks for a team of 2-3 engineers, with moderate complexity due to custom functions, PuppetDB queries, and multi-level Hiera hierarchy.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, and system utilities with MOTD management and package installation
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom defined types, Puppet functions (ensure_value, normalize_port), Bolt tasks, MOTD template management, OS-specific package lists via Hiera

**profile_app_stack**:
- Description: Full application stack orchestrator for Python web applications with PostgreSQL database, systemd service management, and strict dependency chains
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment, Python virtual environment setup, database URL generation via custom function, Gunicorn configuration, systemd service templates, log rotation, health checks

**profile_haproxy**:
- Description: HAProxy load balancer profile with SSL termination, multi-backend support, stats interface, and PuppetDB-based service discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: Dynamic backend configuration, SSL/TLS with custom ciphers, stats dashboard with authentication, firewall integration, custom error pages, 21-level Hiera hierarchy

**profile_postgresql**:
- Description: PostgreSQL database server installation and configuration with version-specific package management
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: Repository management, version-specific packages, service management, OS-family specific configuration

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB-based node discovery and memory management policies
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB queries for cluster member discovery, memory policy configuration, password authentication, custom Facter facts

**puppetdb_query_stub**:
- Description: PuppetDB query function stub for testing environments without active PuppetDB
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Mock PuppetDB query responses, testing infrastructure support

**role**:
- Description: Role definitions that combine profiles into complete node configurations (app_server, app_stack, haproxy, redis_cluster)
- Path: site-modules/role
- Technology: Puppet
- Key Features: Profile orchestration, dependency management, OS-specific path configuration

### Infrastructure Files

- `Puppetfile`: Forge module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, apt
- `environment.conf`: Module path configuration for site-modules and external modules
- `hiera.yaml`: 4-level hierarchy (nodes, OS family, environment, common) with YAML backend
- `data/`: Hiera data with environment-specific overrides and OS-family configurations
- `manifests/site.pp`: Node classification and test application repository setup
- `Vagrantfile`: Development environment configuration
- `test/`: Container-based testing infrastructure

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Debian 11/12, Ubuntu 22.04/24.04 (based on metadata.json operatingsystem_support)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with Ansible community.general collection and custom filters
- **puppetlabs-concat (9.0.2)**: Replace with Ansible template module and file assembly techniques
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw modules
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis role
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt_repository and apt modules

### Security Considerations

- **Hardcoded Credentials**: Multiple modules contain test passwords in Hiera data (haproxy stats, database, Redis, application secret key) - implement Ansible Vault for production
- **SSL/TLS Configuration**: HAProxy module includes SSL cipher suites and certificate paths - migrate to ansible-vault encrypted variables
- **SSH Hardening**: Common.yaml contains SSH security settings (permit_root_login: false, client_alive_interval) - convert to ansible.posix.sshd_config module
- **Service Authentication**: Database credentials, Redis passwords, and application secrets visible in Hiera - requires vault migration strategy
- **Certificate Management**: SSL certificate paths referenced in HAProxy configuration - implement certificate deployment automation

### Technical Challenges

- **PuppetDB Query Migration**: profile_redis_cluster uses PuppetDB queries for cluster member discovery - replace with Ansible inventory groups or dynamic inventory scripts
- **Custom Puppet Functions**: base_utils contains custom functions (ensure_value, normalize_port) and profile_app_stack has app_db_url function - reimplement as Ansible filters or lookup plugins
- **Hiera Hierarchy Complexity**: 21-level hierarchy in HAProxy module with node, cluster, datacenter, environment, and OS-specific data - flatten to Ansible group_vars and host_vars structure
- **Template Engine Migration**: ERB and EPP templates need conversion to Jinja2 with different syntax for conditionals and loops
- **Dependency Chain Management**: Strict dependency chains (python -> database -> app -> service -> monitoring) need conversion to Ansible handlers and task dependencies
- **Bolt Task Integration**: base_utils includes Bolt tasks for health checks and rolling restarts - convert to Ansible ad-hoc commands or playbooks

### Migration Order

1. **base_utils** (low risk, foundational) - Common utilities and helper functions needed by other modules
2. **profile_postgresql** (moderate complexity) - Database layer with clear boundaries and minimal dependencies
3. **profile_app_stack** (high complexity) - Core application with custom functions and strict dependency chains
4. **profile_haproxy** (high complexity) - Load balancer with PuppetDB integration and complex Hiera hierarchy
5. **profile_redis_cluster** (high complexity) - Cluster configuration requiring PuppetDB query replacement
6. **role definitions** (low complexity) - Simple profile orchestration, migrate after all profiles complete

### Assumptions

- PuppetDB service discovery will be replaced with static Ansible inventory or dynamic inventory plugins
- Test environment setup (site.pp git repository creation) will be converted to separate Ansible playbook for development
- Vagrant-based development environment will be maintained with Ansible provisioning instead of Puppet
- Custom Facter facts (haproxy_version, redis_role, platform_info) will be replaced with Ansible custom facts or setup module extensions
- Multi-environment support (production/staging) will use Ansible inventory groups instead of Puppet environment directories
- Container-based testing will be adapted to use ansible-test or molecule framework
- External Forge modules will be replaced with equivalent Ansible Galaxy collections where available
- Hiera eyaml encryption (if present in production) will be migrated to Ansible Vault
- The 4-level Hiera hierarchy will be flattened to Ansible's group_vars/host_vars structure with appropriate precedence