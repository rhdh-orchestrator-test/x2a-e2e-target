# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains Chef InSpec compliance testing examples integrated with Ansible playbooks, rather than traditional Chef cookbooks. The migration scope is limited as the repository already demonstrates a hybrid Chef InSpec + Ansible approach for compliance automation. The primary migration need is to replace Chef InSpec tests with native Ansible testing capabilities while preserving the compliance validation functionality.

## Module Migration Plan

This repository contains Chef InSpec compliance tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

**chef-and-ansible**:
- Description: Hybrid compliance automation example using Chef InSpec for testing alongside Ansible playbooks for Apache HTTPS configuration and SSL hardening
- Path: chef-and-ansible/
- Technology: Chef InSpec + Ansible
- Key Features: Apache SSL/TLS configuration, self-signed certificate generation, POODLE vulnerability mitigation, compliance verification with InSpec tests

**setup-automate**:
- Description: Chef Automate and Chef Infra Server deployment automation scripts for lab environment setup
- Path: setup-automate/
- Technology: Bash scripts
- Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation, system tuning parameters

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `website_https.yml`: Ansible playbook for Apache HTTPS setup with SSL certificate generation
- `poodle_fix.yml`: Ansible playbook for SSL protocol hardening to mitigate POODLE vulnerability
- `tests/website_https_verify.rb`: InSpec compliance test for HTTPS functionality and SSL protocol validation
- `tests/ssh_profile.rb`: InSpec compliance test for SSH root login security configuration
- `deploy-automate.sh`: Chef Automate deployment script with system configuration
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml), with support for RHEL-based systems (referenced in SSH compliance test)
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml for testing)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible native testing modules (assert, uri, stat, command) or external testing frameworks like Testinfra or Molecule
- **Test Kitchen**: Replace with Ansible Molecule for testing and validation workflows
- **Chef Automate/Server**: Evaluate need for centralized compliance reporting - consider Ansible Tower/AWX or external compliance tools

### Security Considerations

- **SSL/TLS Configuration Management**: Current implementation uses Ansible openssl modules for certificate generation - no migration needed for core functionality
- **Compliance Testing**: InSpec tests validate:
  - SSH root login disabled (STIG compliance)
  - SSL protocol hardening (POODLE mitigation)
  - HTTPS service availability and response validation
- **Secrets Management**: Current implementation uses hardcoded passwords in deployment scripts - requires vault integration for production use
- **Certificate Management**: Self-signed certificates used for testing - production migration should integrate with proper CA or certificate management system

### Technical Challenges

- **InSpec Test Migration**: Converting Ruby-based InSpec controls to Ansible native assertions or alternative testing frameworks
- **Compliance Reporting**: Loss of Chef Automate's compliance dashboard requires alternative reporting solution
- **Test Integration**: Maintaining the same level of compliance validation without InSpec's specialized compliance testing capabilities
- **STIG Compliance**: Preserving detailed compliance metadata and control mappings currently embedded in InSpec tests

### Migration Order

1. **Ansible Playbooks** (already complete - no migration needed)
2. **InSpec Tests to Ansible Tests** (moderate complexity - requires test framework selection)
3. **Chef Server Deployment Scripts** (low complexity - convert to Ansible playbooks or maintain as-is)
4. **Test Kitchen to Molecule** (moderate complexity - testing workflow migration)

### Assumptions

- The primary goal is to eliminate Chef InSpec dependency while maintaining compliance validation capabilities
- Ansible playbooks are already functional and do not require migration
- Test Kitchen workflow needs replacement with Ansible-native testing approach
- Chef Automate/Server deployment scripts may be retained if Chef infrastructure is still needed for other purposes
- Compliance reporting requirements may need to be addressed through alternative solutions
- Current hardcoded credentials are acceptable for lab/testing environments but will need proper secrets management for production
- Ubuntu 20.04 target environment is suitable for the migrated solution
- Self-signed certificates are acceptable for testing scenarios in the migrated solution