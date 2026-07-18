# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance verification
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for HTTPS website deployment and SSL security
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL security hardening, compliance testing via InSpec

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef server setup, user/organization creation, automated deployment

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying HTTPS website. Migration consideration: Can be directly used in Ansible, but should be updated to follow current Ansible best practices.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for SSL security hardening. Migration consideration: Can be directly used in Ansible, but should be updated to follow current Ansible best practices.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website. Migration consideration: Convert to Ansible test or maintain as InSpec test run by Ansible.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security. Migration consideration: Convert to Ansible test or maintain as InSpec test run by Ansible.
- `setup-automate/deploy-automate.sh`: Chef Automate deployment script. Migration consideration: Replace with Ansible role for deploying alternative compliance solution.
- `setup-automate/deploy-chef-server.sh`: Chef Server deployment script. Migration consideration: No direct migration needed as Chef Server won't be used in Ansible-only environment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage in playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment (based on comments in setup scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions or maintain InSpec as a standalone tool called from Ansible
  - Options:
    - Use Ansible's `assert` module for basic compliance checks
    - Use Ansible's `stat`, `command`, and `shell` modules to replicate InSpec tests
    - Keep InSpec as a compliance tool and call it from Ansible using the `command` module
    - Consider migrating to Ansible Lint for static analysis

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for testing Ansible roles with various drivers and verifiers

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with specific security settings
  - Migration approach: Preserve the same SSL security configurations in Ansible roles
  - Ensure TLS 1.2 requirement is maintained (from poodle_fix.yml)

- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Create Ansible role for SSH hardening that implements the same controls
  - Include idempotent checks for SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage
  - Count of credentials detected: 4 (username, longusername, useremail, userpassword) in both setup-automate scripts

### Technical Challenges

- **Compliance Testing**: The repository demonstrates using Chef InSpec with Ansible for compliance testing
  - Challenge: Maintaining compliance testing capabilities without Chef InSpec
  - Mitigation: Either keep InSpec as a standalone tool or implement equivalent tests using Ansible's built-in modules

- **Chef Automate Replacement**: The setup scripts deploy Chef Automate for compliance reporting
  - Challenge: Finding an equivalent compliance reporting solution in the Ansible ecosystem
  - Mitigation: Consider AWX/Tower for reporting or integrate with other compliance tools like OpenSCAP

### Migration Order

1. **Ansible Playbooks** (Low risk, directly usable)
   - Refactor existing playbooks to follow current Ansible best practices
   - Move variables to separate vars files
   - Implement proper role structure

2. **Compliance Testing** (Moderate complexity)
   - Decide on compliance testing approach (keep InSpec or migrate to Ansible native)
   - Implement chosen solution

3. **Chef Automate Replacement** (High complexity)
   - Develop Ansible roles for compliance reporting solution
   - Migrate user and organization management to Ansible inventory

### Assumptions

1. The primary goal is to consolidate on Ansible while maintaining compliance testing capabilities
2. The existing Ansible playbooks are functional and can be used as a starting point
3. Chef InSpec may still be used as a standalone tool called from Ansible if direct equivalents are not available
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. The hardcoded credentials in the setup scripts are for demonstration purposes only and will be replaced with secure alternatives
6. The repository is primarily for demonstration/educational purposes rather than production use
7. No actual Chef cookbooks or recipes need migration, only the InSpec tests and deployment scripts