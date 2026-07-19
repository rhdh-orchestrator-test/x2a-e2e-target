# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a unified Ansible approach. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring HTTPS websites with Apache
3. Chef InSpec tests for compliance verification

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on replacing the Chef Automate/Infra Server deployment scripts with Ansible equivalents and ensuring the InSpec tests can be integrated into an Ansible-based workflow. Estimated timeline: 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security settings, InSpec compliance tests

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash + Chef
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Migration considerations: Already in Ansible format, can be used as-is with minor adjustments.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Migration considerations: Already in Ansible format, can be used as-is.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing. Migration considerations: Update to use Ansible-native testing tools or adapt for continued use with InSpec.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website verification. Migration considerations: Convert to Ansible test format or integrate InSpec tests into Ansible workflow.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Migration considerations: Convert to Ansible test format or integrate InSpec tests into Ansible workflow.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate. Migration considerations: Replace with Ansible playbook for infrastructure setup.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations: Replace with Ansible playbook for infrastructure setup.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for infrastructure management
- **Chef Server CLI**: Replace with Ansible roles for infrastructure management
- **Chef InSpec**: Either:
  1. Continue using InSpec as a compliance tool alongside Ansible
  2. Replace with Ansible-native testing tools like Molecule or ansible-test
  3. Use community modules like `geerlingguy.inspec` to run InSpec from Ansible

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. Migration should maintain or enhance these security settings.
- **SSH Security**: InSpec tests verify SSH root login is disabled. Ensure this security check is maintained in the Ansible workflow.
- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL/TLS certificate references in Apache configuration
  - Count: 2 credential patterns detected in setup-automate scripts

### Technical Challenges

- **InSpec Integration**: Determining the best approach to integrate InSpec tests with Ansible workflows. Mitigation: Evaluate options like ansible-inspec module, Molecule with InSpec verifier, or converting tests to Ansible-native formats.
- **Chef Automate Replacement**: Identifying Ansible equivalents for Chef Automate functionality. Mitigation: Evaluate tools like AWX/Tower, Semaphore, or other Ansible-based infrastructure management solutions.

### Migration Order

1. **chef-and-ansible/website_https.yml and poodle_fix.yml** (low risk, high value): Already in Ansible format, minimal changes needed
2. **InSpec Tests** (moderate complexity): Determine integration strategy and implement
3. **setup-automate scripts** (high complexity): Replace with Ansible playbooks for infrastructure setup

### Assumptions

1. The primary goal is to consolidate on Ansible as the configuration management tool, while potentially retaining InSpec for compliance testing.
2. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs.
3. The security requirements (TLS 1.2, SSH hardening) will remain the same.
4. The Chef Automate and Chef Infra Server functionality needs to be replaced with equivalent Ansible-based solutions.
5. The current hardcoded credentials in setup scripts will be replaced with a more secure approach (Ansible Vault or similar).
6. Test Kitchen will be replaced with Ansible-native testing tools or adapted to work with Ansible.