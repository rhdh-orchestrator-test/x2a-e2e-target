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
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML file used for testing the web server. Can be preserved as-is or incorporated into Ansible templates.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider Ansible's built-in `--check` mode for validation

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible management solutions

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS configuration is maintained during migration.
  - Migration approach: Preserve the SSL configuration in the Ansible playbooks, ensuring TLSv1.2 is enforced.

- **SSH Security**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Convert InSpec tests to Ansible assertions or Molecule tests that verify the same SSH security controls.

- **Self-signed Certificates**: The playbooks generate self-signed certificates.
  - Migration approach: Maintain the same certificate generation logic in Ansible, or consider integrating with Let's Encrypt for production environments.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks.
  - Mitigation: Use Ansible's assert module or Molecule for testing, mapping InSpec resources to equivalent Ansible modules.

- **Chef Automate/Infra Server Deployment**: Converting Chef deployment scripts to Ansible playbooks.
  - Mitigation: Create Ansible roles for deploying alternative infrastructure management tools like AWX/Tower.

### Migration Order

1. **website_https.yml and poodle_fix.yml** (low risk, already Ansible): Verify and optimize existing Ansible playbooks
2. **InSpec Tests** (moderate complexity): Convert to Ansible-native testing
3. **Chef Deployment Scripts** (high complexity): Convert to Ansible playbooks for alternative infrastructure

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need significant changes.
2. The InSpec tests are used primarily for validation and can be replaced with equivalent Ansible testing mechanisms.
3. The deployment scripts for Chef Automate and Chef Infra Server will be replaced with Ansible playbooks that deploy alternative infrastructure management tools.
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
5. The migration is focused on preserving functionality rather than enhancing it.
6. No external dependencies or integrations beyond what's visible in the repository need to be considered.
7. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure credential management in the migrated solution.