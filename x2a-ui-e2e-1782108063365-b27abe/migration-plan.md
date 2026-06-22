# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium
**Primary Focus**: Converting InSpec tests to Ansible-compatible testing frameworks

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-compatible testing framework configuration.
- `index.html`: Sample HTML file used in the website deployment. Can be preserved as-is.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Molecule with Testinfra for infrastructure testing
  - Option 2: Ansible Test for compliance testing
  - Option 3: Continue using InSpec but integrate with Ansible workflows

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and management
  - Ansible Content Collections for configuration management
  - Compliance automation using OpenSCAP or similar tools

### Security Considerations

- **SSL Configuration**: The poodle_fix.yml playbook addresses SSL security by disabling SSLv3 and enabling only TLSv1.2. This security practice should be preserved in the migrated solution.

- **SSH Security**: The ssh_profile.rb InSpec test checks for secure SSH configuration, specifically disabling root login. This security check should be implemented in the Ansible-compatible testing framework.

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically in the website_https.yml playbook, which is a good practice to maintain

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks may require learning new testing paradigms and syntax.
  - Mitigation: Start with simple tests and gradually migrate more complex ones. Consider using Molecule with Testinfra as it has similar capabilities to InSpec.

- **Chef Automate/Infra Server Replacement**: Determining the appropriate Ansible-based replacement for Chef Automate and Infra Server functionality.
  - Mitigation: Evaluate Ansible Tower/AWX features against Chef Automate requirements. Document gaps and develop custom solutions as needed.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes, mainly to align with best practices and integrate with new testing framework.

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert these to Ansible-compatible testing frameworks (Molecule/Testinfra or Ansible Test).

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert these to Ansible playbooks that set up equivalent functionality using Ansible Tower/AWX or other appropriate tools.

4. **Test Kitchen Configuration** (kitchen.yml): Replace with Molecule configuration for testing the migrated Ansible roles and playbooks.

### Assumptions

1. The primary goal is to maintain the same functionality while moving completely to Ansible-based tools.

2. The InSpec tests are used for compliance verification and can be replaced with equivalent functionality in Ansible ecosystem.

3. The deployment scripts for Chef Automate and Chef Infra Server are to be replaced with equivalent Ansible-based deployment automation.

4. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs.

5. There are no external dependencies or integrations not visible in the provided repository.

6. The security requirements represented in the InSpec tests (especially SSH hardening) need to be maintained in the migrated solution.