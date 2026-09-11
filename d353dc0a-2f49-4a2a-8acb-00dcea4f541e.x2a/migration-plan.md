# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 8 modules implementing a multi-tier web application stack. The migration involves converting Puppet profiles and roles to Ansible roles, with moderate complexity due to Hiera data hierarchies, PuppetDB queries, and custom functions. Estimated timeline: 6-8 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: ERB template for MOTD, custom Puppet functions (ensure_value, normalize_port), Bolt tasks for health checks, cross-platform OS support

**profile_app_stack**:
- Description: Full application stack orchestrator with Python application deployment, PostgreSQL integration, and systemd service management
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment via vcsrepo, custom database URL function, strict dependency chains, Gunicorn worker configuration, logrotate integration

**profile_haproxy**:
- Description: HAProxy load balancer with SSL termination, multi-backend support, stats interface, and firewall integration
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: ERB/EPP templates for configuration, PuppetDB service discovery, SSL certificate management, custom error pages, 21-level Hiera hierarchy

**profile_postgresql**:
- Description: PostgreSQL database server installation with PGDG repository management and version pinning
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: APT repository configuration, PostgreSQL 15 installation, service management

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB-based node discovery and memory management
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB queries for cluster member discovery, Redis configuration templating, memory policy configuration

**profile**:
- Description: Thin wrapper profiles that delegate to specific profile modules and provide role composition
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Base OS profile with NTP/syslog/utilities, application stack wrapper, HAProxy wrapper

**role**:
- Description: Role definitions that compose profiles for specific node types (app servers, load balancers)
- Path: site-modules/role
- Technology: Puppet
- Key Features: Linux-specific exec path configuration, profile composition with dependency ordering

**puppetdb_query_stub**:
- Description: PuppetDB query function stub for testing and development environments
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Mock PuppetDB query implementation for non-production environments

### Infrastructure Files

- `Puppetfile`: External module dependencies from Puppet Forge - requires mapping to Ansible Galaxy/collections
- `environment.conf`: Module path configuration - needs translation to ansible.cfg
- `hiera.yaml`: 4-level data hierarchy (node/OS/environment/common) - requires Ansible variable precedence design
- `data/`: Hiera YAML data with environment-specific overrides - needs conversion to Ansible group_vars/host_vars
- `manifests/site.pp`: Node classification logic - requires conversion to Ansible inventory and playbooks
- `Vagrantfile`: Development environment setup - may need updates for Ansible provisioning

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, Debian 11/12 based on metadata.json specifications
- **Virtual Machine Technology**: Not specified in configurations
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin modules and community.general collection
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.template and ansible.builtin.assemble modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom tasks
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository modules

### Security Considerations

- **Hardcoded passwords in Hiera data**: Database passwords, Redis passwords, HAProxy stats passwords, and application secret keys are stored in plain text in YAML files
  - Migration approach: Implement Ansible Vault for sensitive data encryption
- **SSL certificate management**: HAProxy SSL configuration references certificate paths without encryption
  - Migration approach: Use Ansible Vault for certificate storage or integrate with certificate management tools
- **SSH hardening configurations**: SSH settings managed through Hiera data
  - Migration approach: Convert to Ansible ssh hardening roles with encrypted variables
- **Service account credentials**: Application database credentials and service passwords visible in configuration
  - Migration approach: Implement proper secrets management with Ansible Vault or external secret stores

### Technical Challenges

- **PuppetDB service discovery**: profile_redis_cluster uses PuppetDB queries to discover cluster members dynamically
  - Mitigation strategy: Replace with Ansible inventory-based discovery or implement custom lookup plugins for dynamic inventory
- **Custom Puppet functions**: profile_app_stack::app_db_url function builds database connection strings
  - Mitigation strategy: Convert to Jinja2 templates or Ansible custom filters
- **Complex Hiera hierarchy**: 21-level hierarchy in profile_haproxy with node/cluster/datacenter/environment/OS levels
  - Mitigation strategy: Redesign variable precedence using Ansible's group_vars structure and inventory organization
- **Strict dependency chains**: profile_app_stack enforces ordering with -> and ~> operators
  - Mitigation strategy: Use Ansible handlers and task dependencies with notify/listen patterns
- **ERB/EPP template conversion**: Multiple complex templates need conversion to Jinja2
  - Mitigation strategy: Systematic template conversion with testing for configuration equivalence

### Migration Order

1. **base_utils** (low risk, foundational): Simple utility module with minimal dependencies, provides foundation for other modules
2. **profile_postgresql** (moderate complexity): Database layer with clear boundaries, needed by application stack
3. **profile_app_stack** (high complexity): Core application logic with custom functions and strict dependencies
4. **profile_haproxy** (high complexity): Load balancer with complex templating and service discovery
5. **profile_redis_cluster** (highest complexity): Requires PuppetDB replacement and cluster coordination logic

### Assumptions

- The target Ansible environment will use similar OS distributions (RHEL 8/9, Ubuntu 22.04/24.04, Debian 11/12) as specified in module metadata
- PuppetDB functionality can be replaced with Ansible inventory-based service discovery or custom lookup plugins
- The existing Hiera data hierarchy can be flattened and reorganized using Ansible's group_vars and host_vars structure
- SSL certificates and private keys will be managed through Ansible Vault or external certificate management systems
- The development team has access to the current Puppet infrastructure for testing migration equivalence
- Custom Puppet functions can be replaced with equivalent Jinja2 templates or Ansible filters without loss of functionality
- The existing Vagrant development environment can be adapted for Ansible testing and validation
- Database and application service credentials can be migrated to Ansible Vault without service disruption
- The current firewall management approach using puppetlabs-firewall can be replaced with appropriate Ansible firewall modules for the target OS distributions