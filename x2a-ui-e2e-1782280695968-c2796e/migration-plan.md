# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the configuration is already in Ansible format. The main migration effort will involve replacing Chef InSpec tests with Ansible-native testing solutions and updating the Chef Automate/Infra Server deployment scripts to use Ansible. Estimated timeline: 1-2 weeks for a small team.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
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
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing. Migration consideration: Can be kept as-is or included as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Use Ansible assert modules for basic compliance checks
  - Option 3: Integrate with other compliance tools like OpenSCAP or Ansible Compliance

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained during migration.
  - Migration approach: Keep the same SSL configuration parameters but use Ansible's apache2_module and apache2_conf modules for more idiomatic configuration.

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Create equivalent checks using Ansible's assert module or Molecule with Testinfra.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions.
  - Mitigation: Use Ansible's assert module for simple tests and Molecule with Testinfra for more complex testing scenarios.

- **Chef Automate Deployment**: Replacing Chef Automate deployment scripts with Ansible playbooks.
  - Mitigation: Create Ansible roles for Chef server deployment or consider migrating to Ansible AWX/Tower instead.

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already in Ansible format)
   - Only need minor updates to follow best practices and current Ansible conventions

2. **InSpec Tests** (moderate complexity)
   - Convert to Ansible assert modules or Molecule with Testinfra
   - Ensure all compliance checks are maintained

3. **Chef Deployment Scripts** (high complexity)
   - Convert to Ansible playbooks or consider replacing with Ansible AWX/Tower deployment

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance testing.
2. The deployment scripts for Chef Automate and Chef Infra Server may be replaced entirely with Ansible AWX/Tower deployment.
3. The target environment will remain Ubuntu 20.04 or be updated to a newer Ubuntu LTS version.
4. The self-signed certificates approach is acceptable for the migrated solution.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure credential management in the production environment.
6. The repository appears to be primarily for demonstration/educational purposes rather than production use.