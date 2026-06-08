# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

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
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance with security standards

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Will need to be updated to use Ansible-native testing frameworks.
- `index.html`: Simple HTML file used for testing web server functionality. Can be preserved as-is.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Molecule with Testinfra for infrastructure testing
  - Option 2: Ansible Test modules (ansible.builtin.assert, ansible.builtin.uri)
  - Option 3: Molecule with Goss for infrastructure testing

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role and playbook testing
  - Option 2: Ansible Test framework for integration testing

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for enterprise automation platform
  - Option 2: Ansible Automation Platform for enterprise automation

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook that disables SSLv3 and enables only TLSv1.2.
- **SSH Security**: The SSH security checks in ssh_profile.rb need to be converted to equivalent Ansible tests.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. This functionality must be preserved in the migrated solution.
- **Vault/secrets management**: 
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require understanding the equivalent assertions and checks.
  - Mitigation: Use Molecule with Testinfra or Goss, which provide similar testing capabilities to InSpec.

- **Chef Automate/Infra Server Deployment**: Converting the Chef deployment scripts to Ansible playbooks will require understanding the Chef Automate and Infra Server installation process.
  - Mitigation: Create Ansible roles for deploying AWX/Ansible Tower or Ansible Automation Platform as replacements.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes, mainly to improve structure and follow best practices.

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert these to Ansible-compatible testing frameworks.

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert these to Ansible playbooks for deploying alternative automation platforms.

4. **Test Kitchen Configuration** (kitchen.yml): Replace with Molecule or Ansible Test configuration.

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functional and follow best practices. If not, they may need refactoring during migration.

2. The InSpec tests are comprehensive and cover all necessary compliance checks. Additional tests may need to be created if gaps are identified.

3. The deployment scripts for Chef Automate and Chef Infra Server are complete and functional. If not, additional research may be needed to ensure the Ansible replacements are equivalent.

4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.

5. The migration will not require changes to the underlying infrastructure or application architecture.

6. The repository appears to be a demonstration or example repository rather than a production system, which may simplify the migration process.

7. No external dependencies or integrations are mentioned in the repository, which simplifies the migration scope.