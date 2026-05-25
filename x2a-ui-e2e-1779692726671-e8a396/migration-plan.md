# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that will need to be replaced with Ansible equivalents.

Estimated timeline: 1-2 weeks for a single developer to complete the migration, with minimal complexity due to the limited scope of Chef components.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-verify**:
    - Description: Chef InSpec test that validates HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec test that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Static HTML content for the web server. Can be preserved as-is and used in Ansible templates.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use the `ansible.builtin.assert` module for basic validation
  - Option 2: Implement Molecule for testing Ansible roles
  - Option 3: Use pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for version control
  - CI/CD pipeline integration for automated testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enabled and older protocols disabled
  - Maintain the same level of Apache security configuration

- **SSH Hardening**: The SSH security checks in ssh_profile.rb must be implemented in Ansible
  - Convert the InSpec control to Ansible assertions or Molecule tests
  - Maintain compliance with the referenced security standards (SRG-OS-000112, RHEL-08-000227)

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username, password)
  - Recommendation: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of assertions
  - Challenge: InSpec has domain-specific language for compliance testing
  - Mitigation: Use Ansible assert module with appropriate conditionals or implement custom modules if needed

- **Chef Server Deployment**: Replacing Chef server deployment scripts with Ansible
  - Challenge: The scripts perform specific Chef-related tasks that don't have direct Ansible equivalents
  - Mitigation: Focus on the outcome (configuration management server) rather than direct translation; consider AWX/Tower deployment

### Migration Order

1. Convert InSpec tests to Ansible tests (low risk, preserves validation capability)
   - website_https_verify.rb → Ansible assertions or Molecule tests
   - ssh_profile.rb → Ansible assertions or Molecule tests

2. Replace kitchen.yml with Molecule configuration (moderate complexity)

3. Create Ansible playbook for Chef Automate/Infra Server replacement (high complexity)
   - Research AWX/Tower deployment options
   - Create playbooks for AWX/Tower installation

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need modification beyond testing framework changes
2. The organization is planning to move completely away from Chef and standardize on Ansible
3. There are no additional Chef cookbooks or resources not visible in the provided repository structure
4. The security compliance requirements (STIG standards referenced in InSpec tests) must be maintained in the Ansible implementation
5. The deployment scripts for Chef Automate/Infra Server are used for development/testing environments and not production
6. No external integrations or dependencies exist beyond what's visible in the repository