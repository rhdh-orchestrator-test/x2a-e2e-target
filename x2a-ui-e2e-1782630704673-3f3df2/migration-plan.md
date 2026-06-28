# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

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
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML file used for testing the web server deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Convert InSpec tests to Ansible roles that perform the same checks

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible management platforms

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook that disables SSLv3 and enables only TLSv1.2.
- **SSH Security**: The SSH root login check in ssh_profile.rb needs to be preserved in the Ansible testing framework.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates, which should be replaced with a more secure certificate management approach in production.
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected (in deploy-automate.sh and deploy-chef-server.sh)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require understanding the equivalent assertions and checks.
  - Mitigation: Use Ansible's assert module for basic checks and consider custom modules for more complex validations.

- **Test Kitchen to Molecule**: The testing workflow will need to be adapted from Test Kitchen to Molecule.
  - Mitigation: Create Molecule scenarios that replicate the Test Kitchen tests.

- **Chef Automate/Server Deployment**: The Chef deployment scripts need to be converted to Ansible playbooks.
  - Mitigation: Create Ansible roles for deploying alternative infrastructure management tools like AWX/Tower.

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need review and potential refactoring to follow best practices.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, need to be converted to Ansible-compatible testing frameworks.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, need to be completely rewritten as Ansible playbooks.

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need functional changes.
2. The InSpec tests are currently used for validation only and don't have any remediation functionality that needs to be preserved.
3. The deployment scripts are used for setting up a test/development environment and not for production deployments.
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
5. There are no external dependencies or integrations not visible in the provided files.
6. The migration will not require changes to the underlying application functionality, only to the infrastructure automation and testing frameworks.
7. The hardcoded credentials in the deployment scripts are for testing purposes and will be replaced with secure credential management in the migrated solution.