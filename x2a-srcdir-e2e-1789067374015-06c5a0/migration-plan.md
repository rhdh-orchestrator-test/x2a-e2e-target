# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles, with a focus on web server and caching service provisioning. The scope is relatively small with minimal complexity, making this an ideal candidate for a straightforward migration with an estimated timeline of 1-2 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic daemon configuration

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with external nginx dependency declaration
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata and platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (explicitly supported in metadata.rb)
- **Virtual Machine Technology**: Not specified in configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **cache (local)**: Convert to Ansible role dependency in requirements.yml

### Security Considerations

- **File permissions**: Static HTML file uses explicit 0644 permissions and root ownership - maintain in Ansible file module
- **Service management**: Both nginx and redis services are enabled and started - ensure proper service state management in Ansible
- **Vault/secrets management**: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared but not resolvable without Berksfile/Policyfile - will need to be handled through Ansible Galaxy or collections
- **Attribute translation**: Chef attributes need conversion to Ansible variables with proper defaults and precedence
- **Service dependency ordering**: Ensure proper task ordering between package installation and service management

### Migration Order

1. **cache cookbook** (low risk, no external dependencies)
2. **simple-nginx cookbook** (moderate complexity due to external nginx dependency)

### Assumptions

- The external nginx dependency will be satisfied by standard Ansible modules rather than requiring a separate nginx role from Ansible Galaxy
- The target environment has package managers (apt/yum) available for nginx and redis installation
- The current Chef cookbook structure represents the complete functionality - no additional recipes or templates are used beyond what's visible in the default recipes
- The metadata-only dependency strategy is for testing purposes and the actual nginx external dependency can be replaced with built-in Ansible modules
- Platform support will be maintained for Ubuntu 18.04+ and CentOS 7+ in the Ansible implementation
- No complex Chef-specific features (encrypted data bags, search, etc.) are used that would complicate the migration