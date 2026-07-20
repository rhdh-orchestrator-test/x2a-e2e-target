# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec tests that need to be consolidated into a pure Ansible solution

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks, as the repository primarily contains deployment scripts and basic web server configurations rather than complex Chef cookbooks.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure HTTPS website with InSpec compliance testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security hardening, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace this with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying an HTTPS website. Can be directly incorporated into the new Ansible structure.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL/TLS vulnerabilities. Can be directly incorporated into the new Ansible structure.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website verification. Should be converted to Ansible testing framework (Molecule).
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Should be converted to Ansible testing framework (Molecule).
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Should be converted to an Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Should be converted to an Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for infrastructure testing
  - Option 2: ansible-lint for static code analysis
  - Option 3: Maintain InSpec as a separate tool but integrate with Ansible workflows

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Determine if a replacement is needed:
  - Option 1: Ansible AWX/Tower for centralized management
  - Option 2: GitLab CI/CD for pipeline-based automation
  - Option 3: Custom solution using Ansible and Git

### Security Considerations

- **SSL/TLS Configuration**: The current implementation focuses on TLS 1.2 and disabling older protocols. Migration should maintain or enhance this security posture.
  - Approach: Use Ansible's `community.crypto` collection for certificate management
  - Ensure the same level of TLS security (TLS 1.2+) is maintained

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions.
  - Approach: Use Ansible's `ansible.posix` collection for SSH configuration management
  - Implement equivalent security controls in Ansible

- **Credentials Management**: The Chef deployment scripts contain hardcoded credentials.
  - Approach: Use Ansible Vault for secure credential storage
  - Replace hardcoded values with variables stored in encrypted files

- **Vault/secrets management**:
  - 1 hardcoded password in setup-automate scripts (userpassword='password')
  - Self-signed certificates generated in the Ansible playbook

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to Ansible-native testing solutions.
  - Mitigation: Use Ansible Molecule with testinfra or goss for similar functionality
  - Create equivalent tests for the current InSpec checks

- **Chef Automate Replacement**: Determining the appropriate replacement for Chef Automate functionality.
  - Mitigation: Evaluate Ansible AWX/Tower as a potential replacement
  - Document the feature gaps between Chef Automate and the chosen Ansible solution

- **Compliance Automation**: Maintaining compliance automation capabilities currently provided by InSpec.
  - Mitigation: Implement compliance checks using Ansible roles and playbooks
  - Consider integrating with OpenSCAP or other compliance tools if needed

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Migrate `website_https.yml` and `poodle_fix.yml` to the new Ansible structure
   - Update any deprecated syntax or modules

2. **Testing Framework** (Medium complexity)
   - Replace Test Kitchen with Ansible Molecule
   - Convert InSpec tests to equivalent Ansible tests

3. **Chef Deployment Scripts** (Higher complexity)
   - Convert `deploy-automate.sh` and `deploy-chef-server.sh` to Ansible playbooks
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary goal is to consolidate on Ansible as the single automation tool, eliminating Chef components.
2. The InSpec tests are valuable and need equivalent functionality in the Ansible solution.
3. The Chef Automate and Chef Infra Server deployments need to be replaced with Ansible-managed alternatives.
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs.
5. The security posture defined in the InSpec tests must be maintained or enhanced.
6. No application-specific configurations beyond the web server are present in the current implementation.
7. The migration will maintain the same level of testing and validation currently provided by InSpec.
8. The hardcoded credentials in the deployment scripts will be replaced with a more secure solution.