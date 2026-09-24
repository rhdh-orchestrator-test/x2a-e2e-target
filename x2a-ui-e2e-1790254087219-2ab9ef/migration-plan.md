# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and documentation but is primarily composed of Ansible playbooks and supporting infrastructure. The migration scope is minimal as the core automation is already implemented in Ansible. The primary work involves consolidating the existing Ansible content and removing Chef-specific deployment scripts in favor of native Ansible solutions.

## Module Migration Plan

This repository contains mixed technologies with Ansible playbooks as the primary automation content and Chef deployment scripts as supporting infrastructure:

### MODULE INVENTORY

**website-https**:
- Description: Apache web server configuration with SSL/TLS termination using self-signed certificates, virtual host setup, and security hardening
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible
- Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, security controls

**poodle-fix**:
- Description: SSL/TLS security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible
- Key Features: Apache SSL protocol configuration, POODLE vulnerability mitigation, service restart handlers

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security profile for SSH root login compliance (STIG control)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `chef-and-ansible/index.html`: Static HTML test content for web server validation

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **apache2 (2.4.41-4ubuntu3.10)**: Already using Ansible apt module - no migration needed
- **openssl**: Already using Ansible openssl_* modules - no migration needed
- **python3-openssl**: Already using Ansible package management - no migration needed
- **Test Kitchen with InSpec**: Consider migrating to ansible-test or molecule for testing framework
- **Chef Automate/Server deployment**: Replace bash scripts with Ansible playbooks for infrastructure deployment

### Security Considerations

- **SSL/TLS Configuration**: Existing playbooks properly implement SSL security controls:
  - Self-signed certificate generation with proper key management
  - SSL protocol hardening (disabling SSL 3.0, enforcing TLS 1.2)
  - File permissions on certificate directories (0640)
- **SSH Hardening**: InSpec profile validates SSH root login restrictions (STIG compliance)
- **Credential Management**: No hardcoded credentials detected in playbooks - uses variables and generated certificates
- **Service Security**: Proper service restart handlers for configuration changes

### Technical Challenges

- **Testing Framework Migration**: Current Test Kitchen + InSpec setup needs evaluation for Ansible-native testing
  - Consider migrating to Molecule for playbook testing
  - Evaluate ansible-test for integration testing
  - Maintain InSpec profiles for compliance validation if required
- **Chef Infrastructure Replacement**: Bash deployment scripts should be converted to Ansible playbooks
  - Create Ansible roles for Chef Automate deployment (if still needed)
  - Implement proper variable management and templating
  - Add idempotency and error handling

### Migration Order

1. **Consolidate Existing Ansible Content** (low risk, immediate value)
   - Organize playbooks into proper Ansible project structure
   - Implement Ansible best practices (roles, group_vars, host_vars)
   - Add proper documentation and variable definitions

2. **Migrate Testing Framework** (moderate complexity)
   - Evaluate Molecule vs Test Kitchen for playbook testing
   - Maintain InSpec compliance tests or migrate to Ansible compliance modules
   - Implement CI/CD pipeline integration

3. **Replace Chef Infrastructure Scripts** (high complexity, optional)
   - Convert bash deployment scripts to Ansible playbooks
   - Only if Chef Automate/Server deployment is still required
   - Consider if this infrastructure is needed in target environment

### Assumptions

- The target environment still requires Apache web server with SSL termination
- InSpec compliance testing framework should be maintained for security validation
- Chef Automate/Server deployment may not be needed in the target Ansible-managed environment
- Ubuntu 20.04 LTS remains the target operating system (may need updating to newer LTS version)
- Test Kitchen integration is acceptable or can be replaced with Molecule
- Self-signed certificates are acceptable for the use case (production may require CA-signed certificates)
- The existing security controls (POODLE fix, SSH hardening) are still relevant and required
- No external Chef cookbooks or dependencies exist that require migration
- The repository serves as examples/documentation rather than production automation code