# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with 5 custom site modules implementing a multi-tier application stack architecture. The migration involves converting role-based profiles for application servers, load balancers, databases, and caching layers. Estimated timeline: 6-8 weeks for a team of 2-3 engineers, with moderate complexity due to PuppetDB queries, custom functions, and multi-level Hiera hierarchy.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with cross-platform support
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom defined types, Puppet functions, Bolt tasks, platform-specific package lists via Hiera, MOTD template management

**profile_app_stack**:
- Description: Full application stack orchestrator for Python applications with PostgreSQL backend, systemd service management, and strict dependency ordering
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository deployment via vcsrepo, custom database URL function, environment-specific configuration templates, logrotate integration, health check scripts

**profile_haproxy**:
- Description: HAProxy load balancer profile with SSL termination, multi-backend support, statistics interface, and optional PuppetDB-based service discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: Dynamic backend configuration via Hiera deep merge, SSL/TLS configuration, firewall integration, custom error pages, stats authentication

**profile_postgresql**:
- Description: PostgreSQL database server installation with PGDG repository management and version pinning for Debian/Ubuntu systems
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: APT repository management, version-specific package installation, service management

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB node discovery, memory management policies, and cluster-aware configuration
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB queries for node discovery, memory policy configuration, cluster topology management

**role**:
- Description: Role composition layer that combines base profiles with service-specific profiles using dependency ordering
- Path: site-modules/role
- Technology: Puppet
- Key Features: Role-based node classification, profile composition, Linux-specific exec path defaults

### Infrastructure Files

- `Puppetfile`: Forge module dependencies including stdlib, concat, firewall, vcsrepo, redis, systemd, inifile, and apt modules
- `environment.conf`: Module path configuration defining site-modules precedence over Forge modules
- `hiera.yaml`: 4-level hierarchy (node → OS family → environment → common) for configuration data
- `data/`: Hierarchical configuration data with environment-specific overrides and OS-specific package lists
- `manifests/site.pp`: Main site manifest for node classification (not examined but likely contains role assignments)
- `Vagrantfile`: Development environment configuration for local testing
- `test/`: Container-based testing infrastructure with Containerfile and test runner

### Target Details

- **Operating System**: Red Hat Enterprise Linux 8/9, Ubuntu 22.04/24.04, Debian 11/12 based on metadata.json operatingsystem_support declarations
- **Virtual Machine Technology**: Not specified in configuration files
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin and community.general modules for common utilities
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.template and ansible.builtin.assemble for file concatenation
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or ansible.builtin.iptables modules
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module for repository management
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules or custom Redis configuration tasks
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module for service management
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt_repository and ansible.builtin.apt modules

### Security Considerations

- **Hardcoded credentials in Hiera data**: Database passwords, Redis passwords, HAProxy stats passwords, and application secret keys are stored in plain text in data/common.yaml
- **SSL/TLS certificate management**: HAProxy profile references SSL certificate and key paths that need secure deployment mechanisms
- **SSH hardening configurations**: SSH client alive intervals and root login restrictions configured via Hiera
- **Application secrets**: Database URLs, API keys, and session secrets managed through environment variable templates
- **Credential patterns per module**:
  - profile_app_stack: Database credentials, application secret keys (4 credential types)
  - profile_haproxy: Stats interface authentication, SSL certificates (2 credential types)
  - profile_redis_cluster: Redis authentication passwords (1 credential type)

### Technical Challenges

- **PuppetDB queries for service discovery**: profile_redis_cluster uses PuppetDB queries to discover cluster nodes, requiring replacement with Ansible inventory or dynamic inventory scripts
- **Custom Puppet functions**: profile_app_stack::app_db_url function needs conversion to Ansible Jinja2 templates or custom filters
- **Multi-level Hiera hierarchy**: 4-level hierarchy (node → OS → environment → common) with deep hash merging needs mapping to Ansible group_vars and host_vars structure
- **Strict dependency ordering**: profile_app_stack enforces strict class dependency chains that need conversion to Ansible task dependencies and handlers
- **Cross-platform package management**: OS-specific package lists in Hiera data need conversion to Ansible when/vars conditionals
- **Template variable scoping**: Puppet ERB templates access class variables that need mapping to Ansible variable namespaces

### Migration Order

1. **base_utils** (low risk, foundational): Common utilities and helper functions, no external service dependencies
2. **profile_postgresql** (moderate complexity): Database foundation required by application stack, straightforward package/service management
3. **profile_redis_cluster** (high complexity): Requires PuppetDB query replacement and cluster discovery mechanism
4. **profile_app_stack** (high complexity): Complex dependency chain, custom functions, and integration with database
5. **profile_haproxy** (moderate complexity): Load balancer configuration with backend discovery dependencies
6. **role** (low complexity): Simple composition layer, migrate after all profiles are complete

### Assumptions

- The site.pp manifest contains node classification logic that assigns roles to nodes based on certname or facts
- PuppetDB is actively used in the environment for the Redis cluster node discovery functionality
- SSL certificates referenced in HAProxy configuration are managed externally or through a separate certificate management system
- The application deployed by profile_app_stack is a Python web application compatible with gunicorn or similar WSGI servers
- Environment-specific Hiera data (production.yaml, staging.yaml) contains environment-specific overrides not visible in common.yaml
- The Vagrant and test infrastructure suggests this is actively developed code with existing CI/CD processes
- Custom facts (base_utils_info.rb, haproxy_version.rb, redis_role.rb) provide runtime information that may need replacement with Ansible facts or custom fact gathering
- The backup.sh and healthcheck.sh scripts in profile_app_stack are functional and can be migrated as-is to Ansible file deployments