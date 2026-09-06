# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both a main cookbook and a local dependency, making it an excellent candidate for establishing migration patterns and testing Ansible conversion workflows.

**Migration Complexity**: Low to Medium
**Estimated Timeline**: 1-2 weeks
**Team Coordination**: Minimal (2 cookbooks, straightforward dependencies)

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All paths have been verified using directory listing and file search tools.

- **simple-nginx**:
    - Description: Simple nginx web server installation with basic configuration, service management, and custom index page creation
    - Path: . (root cookbook)
    - Technology: Chef
    - Key Features: Package installation, service enablement, static file creation, attribute-driven configuration for port and worker processes

- **cache**:
    - Description: Redis cache server installation and service management as a local dependency
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis package installation, service enablement and startup, basic cache infrastructure

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependencies on 'cache' (local) and 'nginx' (external) - requires dependency resolution strategy
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes) - needs conversion to Ansible variables
- `recipes/default.rb`: Main nginx installation and configuration logic
- `cookbooks/cache/recipes/default.rb`: Redis installation and service management
- `README.md`: Documentation explaining metadata-only dependency strategy for X2A Convertor testing

### Target Details

Based on the source configuration analysis:

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (explicitly supported in metadata.rb files)
- **Virtual Machine Technology**: Not specified in configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **cache (local cookbook)**: Convert to Ansible role or include tasks directly in playbook
- **nginx (external dependency)**: Replace with community.general.nginx or geerlingguy.nginx Ansible role from Ansible Galaxy
- **redis-server package**: Use ansible.builtin.package module with platform-specific package names
- **nginx package**: Use ansible.builtin.package module with platform-specific handling

### Security Considerations

- **File permissions**: The cookbook creates `/var/www/html/index.html` with mode 0644, root:root ownership - ensure Ansible maintains proper file permissions
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module handles startup dependencies correctly
- **Package installation**: No specific security configurations detected, standard package management security applies
- **Vault/secrets management**: No credentials, encrypted data bags, or secrets detected in either cookbook

### Technical Challenges

- **Dependency Resolution**: The main cookbook depends on both a local 'cache' cookbook and external 'nginx' cookbook - need to establish clear Ansible role dependency patterns
- **Attribute Translation**: Chef attributes in `attributes/default.rb` need conversion to Ansible variables with proper precedence handling
- **Platform Support**: Both cookbooks support Ubuntu and CentOS - ensure Ansible playbooks handle package name differences (redis-server vs redis)
- **Service Dependencies**: Redis and nginx services need proper startup ordering if used together
- **Testing Strategy**: Original cookbook was designed for "metadata-only dependency strategy" testing - migration testing approach needs definition

### Migration Order

1. **cache cookbook** (Priority 1: Simple, no dependencies, foundational service)
   - Convert redis installation and service management
   - Establish Ansible role structure patterns
   - Test on both Ubuntu and CentOS platforms

2. **simple-nginx cookbook** (Priority 2: Depends on cache, more complex configuration)
   - Convert nginx installation and configuration
   - Implement attribute-to-variable translation
   - Handle file creation and service management
   - Integrate with converted cache role

### Assumptions

- The external 'nginx' dependency mentioned in metadata.rb is not present in the repository and will need to be replaced with an appropriate Ansible Galaxy role
- The cookbook is designed for testing purposes (X2A Convertor validation) but should be migrated as production-ready Ansible code
- Platform support should be maintained for Ubuntu 18.04+ and CentOS 7.0+ as specified in the original metadata
- The simple nature of both cookbooks suggests this is a learning/testing repository rather than production infrastructure
- No complex Chef-specific features (encrypted data bags, custom resources, libraries) are present, simplifying the migration
- Service startup order between redis and nginx is not explicitly defined and may need clarification
- The metadata-only dependency strategy being tested may not have direct Ansible equivalent and needs architectural decision