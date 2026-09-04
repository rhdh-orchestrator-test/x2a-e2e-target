# MIGRATION FROM CHEF INSPEC + ANSIBLE TO PURE ANSIBLE

This repository contains a hybrid Chef InSpec and Ansible demonstration setup that showcases compliance automation patterns. The migration involves consolidating the testing and provisioning workflows into a pure Ansible solution with integrated compliance checking. The scope is limited but requires careful consideration of testing methodologies and compliance frameworks.

**Timeline Estimate**: 1-2 weeks
**Complexity**: Low to Medium
**Risk Level**: Low (demonstration code, no production dependencies)

## Module Migration Plan

This repository contains Chef InSpec compliance tests alongside Ansible playbooks that need consolidation into a unified Ansible-based solution:

### MODULE INVENTORY

**apache-https-setup**:
- Description: Apache web server configuration with SSL/TLS setup, self-signed certificate generation, and virtual host management for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible Playbook
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation, directory structure creation

**ssl-security-hardening**:
- Description: SSL/TLS security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml  
- Technology: Ansible Playbook
- Key Features: POODLE vulnerability mitigation, SSL protocol configuration, Apache SSL module hardening

**compliance-verification-suite**:
- Description: Chef InSpec compliance tests for HTTPS functionality and SSH security hardening verification
- Path: chef-and-ansible/tests/
- Technology: Chef InSpec
- Key Features: Port 443 listening verification, HTTPS response validation, SSL protocol compliance checks, SSH root login security controls

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `index.html`: Static HTML test content for web server validation
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for testing infrastructure
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (as specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with ansible-lint, molecule testing framework, and Ansible's built-in assert module for compliance verification
- **Test Kitchen**: Replace with Molecule for infrastructure testing and validation
- **Vagrant Driver**: Maintain Vagrant compatibility or migrate to Docker/Podman for faster testing cycles
- **OpenSSL Python Module**: Already present in Ansible playbook (python3-openssl package)

### Security Considerations

- **SSL Certificate Management**: Current implementation uses self-signed certificates generated via Ansible's openssl modules - this pattern can be maintained or enhanced with proper CA integration
- **SSH Hardening Verification**: InSpec control "Ensure_SSH_root_login_is_disabled" needs translation to Ansible assert tasks or custom validation modules
- **Compliance Framework Integration**: Current STIG/CCI references in InSpec tests need mapping to Ansible compliance roles or custom validation tasks
- **Credential Management**: No hardcoded credentials detected - deployment scripts use variables that should be externalized to Ansible Vault

### Technical Challenges

- **InSpec to Ansible Translation**: Converting Ruby-based InSpec controls to Ansible validation tasks requires rewriting test logic in YAML/Jinja2
- **Compliance Reporting**: InSpec provides structured compliance reporting that needs equivalent functionality in Ansible (potentially using ansible-runner or custom reporting modules)
- **Test Kitchen Integration**: Current Vagrant-based testing workflow needs migration to Molecule with equivalent test scenarios
- **SSL Protocol Testing**: InSpec's SSL protocol verification capabilities need equivalent implementation using Ansible's uri module or custom validation tasks

### Migration Order

1. **apache-https-setup** (Priority 1: Already in Ansible, requires validation enhancement)
2. **ssl-security-hardening** (Priority 2: Simple Ansible playbook, add compliance verification)
3. **compliance-verification-suite** (Priority 3: Complex InSpec to Ansible translation required)

### Assumptions

- The target environment will maintain Ubuntu 20.04 LTS compatibility for existing package versions
- Vagrant-based testing infrastructure can be preserved or easily migrated to alternative testing frameworks
- Chef Automate deployment scripts are for testing infrastructure only and not part of the core migration scope
- Self-signed certificate approach is acceptable for demonstration purposes and doesn't require CA integration
- SSH hardening requirements follow standard security baselines and don't require custom compliance frameworks
- The "myhost" inventory target represents a generic server that can be parameterized for multiple environments
- Test Kitchen's ansible_playbook provisioner configuration indicates the playbooks are already functional and tested
- InSpec test assertions can be adequately replaced with Ansible's built-in validation capabilities without loss of compliance verification depth