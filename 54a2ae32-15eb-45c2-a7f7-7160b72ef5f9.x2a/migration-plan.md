# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 8 custom modules implementing a multi-tier application stack. The migration involves converting Puppet profiles, roles, and Hiera data to Ansible playbooks, roles, and variables. Estimated timeline: 6-8 weeks for a team of 2-3 engineers, with 2-3 weeks for testing and validation.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: MOTD template management, utility package installation, custom Puppet functions (ensure_value, normalize_port), Bolt tasks for health checks

**profile_app_stack**:
- Description: Full application stack orchestrator with Python application deployment, PostgreSQL integration, and systemd service management
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment via vcsrepo, database URL generation, systemd service configuration, log rotation, environment file templating, strict dependency chain orchestration

**profile_haproxy**:
- Description: HAProxy load balancer with SSL termination, multi-backend support, stats interface, and PuppetDB-based service discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: SSL/TLS configuration, custom error pages, stats authentication, firewall integration, backend configuration templating, optional PuppetDB node discovery

**profile_postgresql**:
- Description: PostgreSQL database server installation with PGDG repository management and version pinning
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: PGDG repository configuration, version-specific package installation, service management

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB-based node discovery and memory management
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB query integration for cluster member discovery, memory policy configuration, password authentication

**puppetdb_query_stub**:
- Description: PuppetDB query function stub for testing environments without PuppetDB
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Mock PuppetDB query function for development/testing

**profile**:
- Description: Namespace module containing profile classes for base OS configuration and application stack delegation
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Base OS profile with NTP/syslog management, application stack wrapper profile

**role**:
- Description: Role classes defining complete node configurations by combining multiple profiles
- Path: site-modules/role
- Technology: Puppet
- Key Features: App server role, app stack role, HAProxy role, Redis cluster role with profile orchestration

### Infrastructure Files

- `Puppetfile`: External module dependencies from Puppet Forge - requires mapping to Ansible Galaxy/collections
- `hiera.yaml`: 4-level Hiera hierarchy (node → OS → environment → common) - needs conversion to Ansible variable precedence
- `environment.conf`: Module path configuration - maps to Ansible roles path structure
- `data/common.yaml`: Global configuration variables including passwords and application settings
- `data/environment/*.yaml`: Environment-specific overrides for production/staging
- `manifests/site.pp`: Main site manifest - equivalent to Ansible site.yml playbook
- `Vagrantfile`: Development environment setup - may need updating for Ansible provisioning

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, Debian 11/12 (based on metadata.json operatingsystem_support)
- **Virtual Machine Technology**: Not specified in configuration files
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin collection and community.general
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.assemble or template concatenation
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis role
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and apt_repository modules

### Security Considerations

- **Hardcoded Passwords**: Multiple plaintext passwords found in Hiera data:
  - HAProxy stats password: "test-haproxy-password"
  - Database password: "test-db-password" 
  - Redis password: "test-redis-password"
  - Application secret key: "test-secret-key"
  - Migration approach: Implement Ansible Vault for all credential storage
- **SSL/TLS Configuration**: HAProxy module includes SSL certificate management requiring secure certificate deployment patterns
- **SSH Hardening**: SSH configuration in Hiera (permit_root_login: false, client_alive_interval) needs conversion to ansible.posix.sshd_config
- **Service Authentication**: Stats interfaces and database connections use password authentication requiring vault integration

### Technical Challenges

- **PuppetDB Integration**: profile_redis_cluster uses PuppetDB queries for node discovery - requires replacement with Ansible inventory or dynamic inventory scripts
- **Custom Puppet Functions**: profile_app_stack::app_db_url function needs conversion to Ansible Jinja2 filters or custom modules
- **Strict Dependency Chains**: Complex dependency relationships (Class['A'] -> Class['B'] ~> Class['C']) need careful conversion to Ansible handler patterns and task ordering
- **Hiera Hierarchy**: 4-level hierarchy with automatic parameter lookup needs conversion to Ansible variable precedence and group_vars structure
- **Template Complexity**: ERB templates with complex logic need conversion to Jinja2 with equivalent functionality
- **Bolt Tasks**: Health check and rolling restart tasks need conversion to Ansible modules or shell commands

### Migration Order

1. **base_utils** (low risk, foundational) - Simple utility installation and MOTD management
2. **profile_postgresql** (moderate complexity) - Database installation with repository management
3. **profile** (low complexity) - Base OS configuration profiles
4. **profile_app_stack** (high complexity) - Complex application deployment with dependencies
5. **profile_haproxy** (high complexity) - Load balancer with SSL and discovery features
6. **profile_redis_cluster** (highest complexity) - Requires PuppetDB replacement strategy
7. **role** (integration phase) - Role composition after all profiles are migrated
8. **puppetdb_query_stub** (testing support) - Convert to Ansible testing utilities

### Assumptions

- Test passwords in Hiera data will be replaced with proper secrets management in production
- PuppetDB functionality can be replaced with Ansible inventory or external service discovery
- Current Vagrant-based development workflow will be maintained with Ansible provisioning
- SSL certificates are managed externally and only referenced by path in HAProxy configuration
- The 4-level Hiera hierarchy maps cleanly to Ansible's group_vars and host_vars structure
- Custom Puppet functions have equivalent Jinja2 filter implementations or can be replaced with simpler logic
- Bolt task functionality can be replicated with Ansible ad-hoc commands or playbook tasks
- Operating system support matrix remains the same for Ansible roles (RHEL 8/9, Ubuntu 22.04/24.04, Debian 11/12)