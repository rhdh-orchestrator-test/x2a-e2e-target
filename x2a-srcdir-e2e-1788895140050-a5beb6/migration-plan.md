# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles, with a focus on web server and caching service provisioning. The scope is relatively small but demonstrates key Chef-to-Ansible migration patterns including local dependencies, package management, and service configuration.

**Estimated Timeline**: 1-2 weeks for a small team
**Complexity**: Low to Medium (simple cookbooks with basic dependencies)

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx web server installation with basic configuration, custom index page, and service management
    - Path: . (root cookbook)
    - Technology: Chef
    - Key Features: Package installation, service enablement, static file deployment, attribute-driven configuration

- **cache**:
    - Description: Redis server installation and configuration for caching services
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata with dependencies on 'cache' and 'nginx' cookbooks
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy testing purpose

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx modules
- **cache (local)**: Convert to Ansible role with redis installation and configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: Static HTML file created with explicit 0644 permissions and root ownership - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module configurations maintain security best practices
- **Package sources**: No custom repositories or package sources identified - standard distribution packages used

### Technical Challenges

- **Dependency resolution**: The cookbook depends on an external 'nginx' cookbook not present in the repository - will need to implement nginx configuration directly in Ansible or source appropriate role
- **Attribute translation**: Chef attributes (nginx port, user, worker processes) need conversion to Ansible variables with appropriate defaults
- **Service ordering**: Ensure proper service startup order between nginx and redis in Ansible playbooks
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS as specified in original metadata

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Convert redis installation and service management to Ansible role
2. **simple-nginx cookbook** (moderate complexity) - Convert nginx installation, configuration, and static content deployment
3. **Integration testing** - Verify both roles work together and maintain original functionality

### Assumptions

- The external 'nginx' cookbook dependency will be replaced with direct Ansible nginx configuration rather than sourcing a separate role
- Current attribute values in `attributes/default.rb` represent production-ready defaults that should be preserved
- The repository is used for testing metadata-only dependency strategies, so the migration should maintain the same architectural patterns in Ansible
- No encrypted data bags, vault configurations, or complex secrets management is present based on the simple cookbook structure
- The target environment will use the same package names (nginx, redis-server) as the source Chef cookbooks
- Service management patterns (enable + start) should be preserved in the Ansible migration