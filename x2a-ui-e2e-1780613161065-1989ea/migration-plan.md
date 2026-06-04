# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native solutions while preserving the existing Ansible playbooks. The repository also includes Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible.

Estimated timeline: 1-2 weeks for a small team (1-2 engineers) to complete the migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables TLSv1.2 only

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security requirements (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used for testing the web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-lint for static analysis of playbooks
  - Option 2: Use Molecule for testing Ansible roles and playbooks
  - Option 3: Use pytest-ansible for Python-based testing of Ansible deployments

- **Test Kitchen**: Replace with Molecule for testing Ansible roles and playbooks
  - Molecule provides similar functionality for Ansible-native testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain self-signed certificate generation process

- **SSH Security**: Preserve the SSH root login restriction check
  - Convert the InSpec control to an Ansible-based check or Molecule test

- **Credentials Management**: 
  - The Chef deployment scripts contain hardcoded credentials that should be moved to Ansible Vault
  - Count: 3 credentials detected (username, userpassword, useremail)

### Technical Challenges

- **Compliance Testing**: Converting InSpec tests to Ansible-native testing solutions
  - Challenge: InSpec provides a domain-specific language for compliance testing that doesn't have a direct equivalent in Ansible
  - Mitigation: Use a combination of ansible-lint, Molecule, and custom Ansible modules to achieve similar compliance testing capabilities

- **Test Kitchen to Molecule Migration**: 
  - Challenge: Test Kitchen configuration needs to be converted to Molecule
  - Mitigation: Create equivalent Molecule scenarios that match the Test Kitchen configuration

- **Chef Automate/Server Deployment**: 
  - Challenge: Converting Chef Automate and Chef Infra Server deployment scripts to Ansible
  - Mitigation: Create Ansible roles that perform equivalent setup tasks, potentially using the `command` or `shell` modules to interact with Chef CLI tools if necessary

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they are already in Ansible format
   - Review and optimize existing playbooks
   - Add documentation and comments

2. **Testing Framework** - Moderate complexity
   - Set up Molecule testing framework
   - Create test scenarios equivalent to the existing Test Kitchen configuration

3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Moderate complexity
   - Convert InSpec tests to Molecule/pytest-ansible tests
   - Ensure all compliance checks are preserved

4. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - High complexity
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need functional changes
2. The target environment will continue to be Ubuntu 20.04 or compatible
3. Vagrant will continue to be used for development/testing environments
4. The Chef InSpec tests are currently used for compliance validation and their functionality needs to be preserved
5. The repository is primarily used for demonstration/educational purposes rather than production deployment
6. The Chef Automate and Chef Infra Server deployment scripts are used for setting up test environments
7. No external dependencies or integrations beyond what's visible in the repository
8. No specific performance requirements for the migrated solution