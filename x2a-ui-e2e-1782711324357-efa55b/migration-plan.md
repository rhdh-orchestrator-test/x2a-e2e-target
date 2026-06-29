# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

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
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality of the Apache web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used as a template for the website. Can be preserved as-is or converted to an Ansible template.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible Test for integration testing

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for enterprise automation
  - Option 2: Ansible Automation Platform

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL configuration is maintained during migration.
  - Migration approach: Preserve the existing SSL configuration in the Ansible playbooks.

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Convert InSpec tests to Ansible assert statements or Molecule tests.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault.
  - Self-signed certificates are generated in the playbook and should be handled securely.
  - Document the count and type of credentials detected per module:
    - chef-automate-deployment: 3 credentials (username, password, organization)
    - chef-server-deployment: 3 credentials (username, password, organization)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks may require learning new testing methodologies.
  - Mitigation: Start with simple assertions and gradually add more complex tests.

- **Chef Automate/Infra Server Deployment**: Converting the Chef deployment scripts to Ansible playbooks requires understanding of Chef Automate architecture.
  - Mitigation: Research Ansible roles for Chef deployment or create custom roles based on the existing scripts.

### Migration Order

1. **Preserve Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml) - low risk, high value
   - These are already in Ansible format and can be used as-is.

2. **Convert InSpec Tests to Ansible Tests** (website_https_verify.rb, ssh_profile.rb) - moderate complexity
   - Convert to Ansible assertions or Molecule tests.

3. **Convert Chef Deployment Scripts to Ansible Playbooks** (deploy-automate.sh, deploy-chef-server.sh) - high complexity
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment.

4. **Replace Test Kitchen with Ansible-native Testing** (kitchen.yml) - moderate complexity
   - Set up Molecule or another Ansible testing framework.

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need significant changes.
2. The InSpec tests are currently used for compliance verification and need to be preserved in some form.
3. The Chef Automate and Chef Infra Server deployment scripts are still needed and should be converted to Ansible.
4. The target environment will continue to be Ubuntu 20.04 or compatible.
5. The repository is primarily used for demonstration purposes rather than production deployment.
6. No external dependencies or complex integrations exist beyond what's visible in the repository.
7. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure alternatives.