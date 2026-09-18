# MIGRATION FROM PUPPET TO ANSIBLE

This repository contains a Puppet control repository with a sophisticated role/profile pattern implementation managing a multi-tier application stack. The migration involves 8 distinct modules with complex interdependencies, hierarchical data management, and PuppetDB integration. Estimated timeline: 8-12 weeks for a team of 2-3 engineers, with 2-3 weeks for testing and validation.

## Module Migration Plan

This repository contains Puppet modules that need individual migration planning:

### MODULE INVENTORY

**base_utils**:
- Description: Base utility module providing common helper types, functions, MOTD management, and utility package installation with OS-specific data
- Path: site-modules/base_utils
- Technology: Puppet
- Key Features: Custom functions (ensure_value, normalize_port), Facter facts, Bolt tasks, ERB templates, OS-specific Hiera data

**profile_app_stack**:
- Description: Full application stack orchestrator managing Python application deployment with PostgreSQL database, systemd service, and monitoring
- Path: site-modules/profile_app_stack
- Technology: Puppet
- Key Features: Git repository cloning, Python virtual environment, Gunicorn WSGI server, database URL generation via custom function, strict dependency chain, environment-specific configuration

**profile_haproxy**:
- Description: HAProxy load balancer with SSL termination, multi-backend support, stats interface, and PuppetDB-based service discovery
- Path: site-modules/profile_haproxy
- Technology: Puppet
- Key Features: 21-level Hiera hierarchy, dynamic backend configuration, SSL/TLS with custom ciphers, firewall integration, custom error pages, stats authentication

**profile_postgresql**:
- Description: PostgreSQL database server installation with PGDG repository management and version pinning
- Path: site-modules/profile_postgresql
- Technology: Puppet
- Key Features: APT repository configuration, package version control, service management

**profile_redis_cluster**:
- Description: Redis cluster configuration with PuppetDB node discovery and memory management policies
- Path: site-modules/profile_redis_cluster
- Technology: Puppet
- Key Features: PuppetDB queries for cluster member discovery, memory policy configuration, password authentication

**profile**:
- Description: Wrapper profile classes implementing the role/profile pattern with thin delegation layers
- Path: site-modules/profile
- Technology: Puppet
- Key Features: Environment fact integration, delegation to concrete profile modules, role composition

**role**:
- Description: Role definitions combining multiple profiles for complete node configurations
- Path: site-modules/role
- Technology: Puppet
- Key Features: Multi-profile composition, dependency ordering, OS-specific path configuration

**puppetdb_query_stub**:
- Description: PuppetDB query function stub for testing and development environments
- Path: site-modules/puppetdb_query_stub
- Technology: Puppet
- Key Features: Mock PuppetDB query functionality for non-production environments

### Infrastructure Files

- `Puppetfile`: External module dependencies from Puppet Forge (stdlib, concat, firewall, vcsrepo, redis, systemd, inifile, apt)
- `environment.conf`: Module path configuration defining search order for modules
- `hiera.yaml`: 4-level hierarchical data configuration (node → OS → environment → common)
- `data/`: Hierarchical configuration data with environment-specific overrides
- `manifests/site.pp`: Main site manifest with node classification and test application setup
- `Vagrantfile`: Development environment provisioning
- `test/`: Container-based testing infrastructure

### Target Details

- **Operating System**: Red Hat Enterprise Linux 9 and Ubuntu 24.04 LTS (based on metadata.json operatingsystem_support)
- **Virtual Machine Technology**: Not specified in configuration
- **Cloud Platform**: Not specified in configuration

## Migration Approach

### Key Dependencies to Address

- **puppetlabs-stdlib (9.7.0)**: Replace with ansible.builtin collection and community.general modules
- **puppetlabs-concat (9.0.2)**: Replace with ansible.builtin.template and ansible.builtin.assemble modules
- **puppetlabs-firewall (8.1.3)**: Replace with ansible.posix.firewalld or community.general.ufw
- **puppetlabs-vcsrepo (6.1.0)**: Replace with ansible.builtin.git module
- **puppet-redis (11.0.0)**: Replace with community.general.redis modules and custom configuration
- **puppet-systemd (7.1.0)**: Replace with ansible.builtin.systemd module
- **puppetlabs-inifile (6.1.1)**: Replace with community.general.ini_file module
- **puppetlabs-apt (9.4.0)**: Replace with ansible.builtin.apt and ansible.builtin.apt_repository modules

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found in common.yaml (haproxy stats, database, Redis, application secret key) - migrate to Ansible Vault
- **SSL/TLS Configuration**: HAProxy SSL certificate paths and cipher suites require secure certificate deployment strategy
- **Database Authentication**: PostgreSQL connection credentials need vault encryption
- **Service Authentication**: Redis password authentication requires secure credential management
- **SSH Hardening**: Existing SSH security configurations (root login disabled, client alive interval) need preservation
- **Firewall Rules**: HAProxy firewall integration requires careful port and rule migration

### Technical Challenges

- **PuppetDB Integration**: profile_redis_cluster uses PuppetDB queries for dynamic node discovery - replace with Ansible inventory plugins or dynamic inventory scripts
- **Custom Puppet Functions**: profile_app_stack::app_db_url function needs conversion to Jinja2 template or custom Ansible filter
- **21-Level Hiera Hierarchy**: Complex data hierarchy (node/cluster/datacenter/environment/OS) requires careful Ansible group_vars and host_vars structure design
- **Strict Dependency Chains**: profile_app_stack enforces strict ordering (python → database → app → service → monitoring) - implement with Ansible handlers and task dependencies
- **ERB/EPP Templates**: Convert Puppet ERB templates to Jinja2, particularly complex haproxy.cfg.erb with conditional SSL blocks
- **Custom Types and Facts**: base_utils custom types (ensure_value, log_level, port) and facts need Ansible equivalents or custom modules
- **Role/Profile Pattern**: Preserve the role/profile abstraction layer in Ansible playbook and role structure

### Migration Order

1. **base_utils** (low risk, foundational) - Common utilities and OS configuration
2. **profile_postgresql** (moderate complexity) - Database foundation for application stack
3. **profile_redis_cluster** (high complexity) - Requires PuppetDB replacement strategy
4. **profile_app_stack** (high complexity) - Core application with multiple dependencies
5. **profile_haproxy** (high complexity) - Load balancer with SSL and discovery features
6. **profile wrapper classes** (low risk) - Thin delegation layers
7. **role definitions** (moderate complexity) - Multi-profile orchestration
8. **puppetdb_query_stub** (low risk) - Testing utility

### Assumptions

- Target environments will use the same OS versions (RHEL 8/9, Ubuntu 22.04/24.04) as specified in module metadata
- PuppetDB functionality can be replaced with Ansible inventory plugins or external service discovery
- SSL certificates referenced in HAProxy configuration are available for deployment via Ansible
- Database and Redis instances will maintain the same network topology and connectivity requirements
- The role/profile pattern abstraction will be preserved in the Ansible implementation
- Custom Puppet functions can be replaced with equivalent Jinja2 filters or custom Ansible modules
- Hiera data hierarchy complexity can be mapped to Ansible's group_vars/host_vars structure
- Test infrastructure (Vagrant, containers) will be adapted to support Ansible playbook testing
- Git repository structure and branching strategy will remain compatible with Ansible deployment workflows