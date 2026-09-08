# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef-based infrastructure setup with two cookbooks focused on web server and caching functionality. The migration scope is relatively small but demonstrates key Chef patterns including local and external dependencies. Estimated timeline: 1-2 weeks for a small team, with low to moderate complexity due to the straightforward nature of the cookbooks and minimal external dependencies.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation and configuration with basic HTML content serving and service management
- Path: . (root level cookbook)
- Technology: Chef
- Key Features: Package installation, service management, static HTML file creation, attribute-driven configuration for port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching functionality
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup, basic caching infrastructure

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata defining simple-nginx cookbook with dependencies on cache and nginx cookbooks
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default attribute definitions for nginx configuration (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy for testing purposes

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in the repository
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, plus nginx Ansible Galaxy collection for advanced configuration
- **cache (local)**: Migrate redis installation and service management to Ansible using ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: Static HTML file creation uses explicit mode (0644) and ownership (root:root) - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module configurations maintain proper service security
- **No secrets identified**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata but not managed by Berksfile or Policyfile - migration will need to determine appropriate nginx Ansible collection or role
- **Attribute translation**: Chef attributes (nginx port, user, worker processes) need conversion to Ansible variables with appropriate defaults and templating
- **Service dependency ordering**: Ensure proper task ordering in Ansible playbooks to maintain the same installation and startup sequence

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple redis installation)
2. **simple-nginx cookbook** (moderate complexity due to external nginx dependency and attribute usage)

### Assumptions

- The external nginx dependency mentioned in metadata.rb will be resolved through Ansible Galaxy collections or community roles rather than custom implementation
- The target environment will maintain the same OS support matrix (Ubuntu 18.04+, CentOS 7+) unless explicitly changed
- The simple HTML content serving approach will be maintained rather than implementing more complex nginx configuration management
- No additional Chef environments, roles, or data bags exist beyond what's visible in this repository structure
- The metadata-only dependency strategy mentioned in README.md is for testing purposes and doesn't indicate complex dependency resolution requirements in production