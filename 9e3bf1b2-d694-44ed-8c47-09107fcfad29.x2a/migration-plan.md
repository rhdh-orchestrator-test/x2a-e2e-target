# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks focused on demonstrating compliance automation alongside infrastructure provisioning. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance verification
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing capabilities while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Collection of Ansible playbooks and InSpec tests for secure website deployment
    - Path: chef-and-ansible
    - Technology: Ansible/InSpec
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef infrastructure deployment, user and organization setup

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website with Apache
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for remediating SSL POODLE vulnerability in Apache
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec tests for verifying HTTPS website functionality and security
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec profile for SSH security compliance
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file for website testing
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server without Automate

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts suggest on-premises or generic cloud VM targets

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - ansible-test for collection testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and management

- **SSH Security**: Preserve the SSH security controls from the InSpec profile
  - Ensure root login remains disabled
  - Consider expanding SSH hardening based on the STIG references

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates should be managed securely, potentially with ansible-vault
  - Count of credentials detected:
    - setup-automate scripts: 3 credentials (username, password, email)

### Technical Challenges

- **InSpec Test Migration**: Converting InSpec tests to equivalent Ansible verification
  - Challenge: InSpec has specialized resources for testing SSL/TLS configurations
  - Mitigation: Use Ansible assert modules with custom commands or consider keeping InSpec for specialized tests

- **Chef Automate/Server Deployment**: Replacing Chef infrastructure deployment
  - Challenge: The current scripts deploy Chef-specific infrastructure
  - Mitigation: Determine if Chef Automate/Server is still needed or if it can be replaced with Ansible Automation Platform

### Migration Order

1. **Ansible Playbooks** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbooks in chef-and-ansible directory
   - Convert any embedded variables to proper Ansible variable files

2. **InSpec tests** (moderate complexity)
   - Convert to Ansible assert tasks where possible
   - For complex tests, create a mechanism to invoke InSpec from Ansible

3. **Chef deployment scripts** (high complexity)
   - Determine if Chef infrastructure is still needed
   - If not, remove these components
   - If yes, create Ansible playbooks to deploy Chef infrastructure

### Assumptions

1. The primary goal is to consolidate on Ansible while maintaining compliance testing capabilities
2. The Chef InSpec tests are valuable and need to be preserved in some form
3. The deployment of Chef Automate/Server may no longer be necessary if fully migrating to Ansible
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Test Kitchen integration is important for the development workflow
6. The security compliance requirements (STIG references) must be maintained
7. The repository is primarily for demonstration/example purposes rather than production use