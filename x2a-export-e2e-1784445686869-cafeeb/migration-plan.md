# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec tests that need to be consolidated into a pure Ansible solution

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks, as the repository contains a limited number of scripts and playbooks with straightforward functionality.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure HTTPS website with Chef InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security settings, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace this with Ansible-native testing solutions like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying an HTTPS website. Can be directly incorporated into the new Ansible structure.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Can be directly incorporated into the new Ansible structure.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Should be migrated to Ansible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Should be migrated to Ansible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs to be converted to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs to be converted to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static code analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider Ansible's built-in `--check` mode with custom reporting

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Determine if a replacement is needed or if this functionality is being retired:
  - Option 1: Use AWX/Ansible Tower as a replacement for Chef Automate
  - Option 2: Use GitLab CI/CD or Jenkins for pipeline automation
  - Option 3: Use Ansible Semaphore for a lightweight Ansible UI

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. Migration should maintain or enhance these security settings.
  - Migration approach: Preserve the same security configurations in the Ansible playbooks, consider upgrading to TLS 1.3 if supported.

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Migration should include equivalent checks.
  - Migration approach: Convert InSpec tests to Ansible assertions or include in Ansible security role.

- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider enhancing with Let's Encrypt integration.
  - Migration approach: Add optional Let's Encrypt support using Ansible's `acme_certificate` module.

- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms.
  - Mitigation strategy: Create a mapping of InSpec resources to Ansible modules and develop a testing framework using Ansible's assert module or Molecule.

- **Chef Automate Functionality**: Ensuring all Chef Automate functionality has an equivalent in the Ansible ecosystem.
  - Mitigation strategy: Document feature parity between Chef Automate and Ansible alternatives (AWX/Tower), identify any gaps that need custom solutions.

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/website_https.yml, chef-and-ansible/poodle_fix.yml)
   - Low risk as they're already in Ansible format
   - Focus on restructuring to follow Ansible best practices (roles, variables)

2. **Testing Framework** (chef-and-ansible/tests/*)
   - Medium complexity
   - Convert InSpec tests to Ansible testing mechanisms

3. **Chef Deployment Scripts** (setup-automate/*)
   - Higher complexity
   - Convert bash scripts to Ansible playbooks
   - Implement secure credential management

### Assumptions

1. The Chef Automate and Chef Infra Server deployment is still needed in the new infrastructure. If not, these components can be omitted from migration.
2. The current testing approach using InSpec is preferred and needs to be maintained in some form. If not, simpler testing approaches could be used.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure alternatives.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The migration will maintain the same level of security compliance as the original implementation.
6. The Vagrant-based testing environment is still relevant for the new implementation.