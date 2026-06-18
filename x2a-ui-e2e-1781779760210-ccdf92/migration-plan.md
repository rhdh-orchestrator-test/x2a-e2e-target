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
    - Description: Chef InSpec test that verifies HTTPS functionality of the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing the web server. No migration needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for simple tests
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Convert InSpec tests to Ansible roles with test tasks

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/Jenkins for pipeline automation
  - Compliance scanning tools like OpenSCAP or Ansible's built-in security roles

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook that disables SSLv3 and enables only TLSv1.2.
- **SSH Security**: The SSH root login compliance check needs to be converted to an equivalent Ansible check.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically but should be managed securely
  - Count of credentials detected: 3 (username, password, organization name in deployment scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's domain-specific language to Ansible's YAML syntax while maintaining the same level of testing capability.
  - Mitigation: Use Ansible's assert module combined with command/shell modules to run equivalent checks.

- **Compliance Reporting**: InSpec provides built-in compliance reporting that needs to be replicated in Ansible.
  - Mitigation: Integrate with tools like OpenSCAP or use custom reporting scripts that parse Ansible output.

- **Chef Server Deployment**: Converting the Chef Server deployment scripts to Ansible requires finding equivalent Ansible roles or creating custom roles.
  - Mitigation: Create Ansible roles that install and configure Ansible AWX/Tower as a replacement for Chef Automate/Server.

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, may need minor adjustments for best practices.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, requires converting Ruby-based tests to Ansible-compatible format.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires replacing Chef-specific functionality with Ansible equivalents.

### Assumptions

1. The primary goal is to move all functionality to Ansible, eliminating dependencies on Chef tools.
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and follow best practices.
3. The target environment will continue to be Ubuntu 20.04 or compatible systems.
4. The team has expertise in both Chef InSpec and Ansible to facilitate the migration.
5. There is no requirement to maintain backward compatibility with Chef tools after migration.
6. The self-signed certificates used in the current setup are acceptable for the migrated solution.
7. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migrated solution.
8. The compliance requirements represented by the InSpec tests need to be maintained in the Ansible solution.