# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec compliance tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

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
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing web server functionality. Can be preserved as-is.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Implement custom Ansible modules for compliance testing
  - Option 3: Use community.general.assert module with appropriate conditions
  - Option 4: Consider integrating with other compliance tools like OpenSCAP

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
  - Molecule provides similar functionality for testing Ansible roles and playbooks
  - Will require new configuration files and test structure

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced
  - Maintain proper certificate generation and management

- **SSH Security**: The SSH root login check must be preserved in the Ansible equivalent
  - Convert the InSpec control to an Ansible task that checks the same configuration

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts (username, password)
  - These should be moved to Ansible Vault during migration

### Technical Challenges

- **InSpec to Ansible Conversion**: Converting InSpec tests to Ansible-compatible verification methods
  - Challenge: InSpec has specific testing constructs that don't directly map to Ansible
  - Mitigation: Use assert module with appropriate conditions or develop custom modules

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Challenge: Ensuring proper sequencing and error handling during installation
  - Mitigation: Break down the installation process into distinct tasks with proper checks

- **Testing Framework**: Replacing Test Kitchen with Molecule
  - Challenge: Different configuration syntax and test execution flow
  - Mitigation: Create a new Molecule configuration that mirrors the existing Test Kitchen setup

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml)
   - Low risk as they're already in Ansible format
   - May need minor updates for best practices and integration with new testing framework

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb)
   - Convert to Ansible verification tasks
   - Integrate with the existing playbooks

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh)
   - Convert to Ansible playbooks
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't require functional changes
2. The InSpec tests are currently used for post-deployment verification and can be replaced with equivalent Ansible verification tasks
3. The deployment scripts are used for setting up Chef infrastructure, which may not be needed after migration to Ansible
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. No external dependencies or integrations beyond what's visible in the repository
6. The migration is primarily focused on replacing Chef InSpec with Ansible-native solutions while preserving the existing Ansible playbooks
7. No custom InSpec resources are being used that would require special handling
8. The repository is primarily for demonstration purposes rather than production use