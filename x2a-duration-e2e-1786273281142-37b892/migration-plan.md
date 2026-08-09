# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and Chef Automate/Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Ansible playbooks that configure web servers with HTTPS
2. Chef InSpec tests for compliance verification
3. Bash scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on converting the InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards

- **automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Static HTML content for the web server. No migration needed, can be used as-is in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Keep InSpec but integrate with Ansible using the `inspec` Ansible module

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Configure system requirements (hostname, sysctl parameters)
  - Install and configure alternative infrastructure management tools (AWX/Tower)

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should ensure:
  - Self-signed certificates are properly generated or replaced with Let's Encrypt integration
  - SSL protocols are properly configured (TLSv1.2 enabled, older protocols disabled)

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Migration should:
  - Incorporate these checks into Ansible-native testing
  - Ensure SSH hardening is applied consistently

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deployment scripts (username/password)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks while maintaining the same level of compliance verification
  - Mitigation: Use Ansible's assert module with custom modules or consider keeping InSpec as a testing tool

- **Chef Automate Replacement**: Determining the appropriate replacement for Chef Automate functionality
  - Mitigation: Evaluate AWX/Tower or other open-source alternatives based on specific requirements

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible-compatible testing
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, requires designing Ansible playbooks to replace Chef infrastructure

### Assumptions

1. The primary goal is to standardize on Ansible and remove Chef dependencies
2. The InSpec tests are valuable and their functionality should be preserved
3. A replacement for Chef Automate/Infra Server is needed (AWX/Tower or similar)
4. The target environment will continue to be Ubuntu 20.04 or compatible
5. Vagrant will continue to be used for development/testing environments
6. The security compliance requirements (SSH configuration, SSL protocols) must be maintained
7. The self-signed certificates approach is acceptable (vs. using Let's Encrypt or commercial certificates)
8. The current Apache configuration meets all requirements and should be preserved