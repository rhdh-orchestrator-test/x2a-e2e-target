# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec test profiles to migrate. The estimated timeline for migration would be 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used for testing the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-lint for static analysis
  - Option 3: Integrate with pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for infrastructure testing
  - Option 2: Use simple Vagrant or Docker-based testing with direct Ansible commands

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Option 1: Migrate to Ansible Automation Platform (formerly Ansible Tower)
  - Option 2: Use AWX (open-source version of Ansible Tower)
  - Option 3: Use GitLab CI/CD or Jenkins with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL/TLS configuration is maintained in the migrated Ansible playbooks.
  - Migration approach: Maintain the same SSL configuration parameters but update to modern best practices if needed.

- **SSH Security**: The InSpec tests verify SSH security configurations. Ensure these checks are maintained in the Ansible testing framework.
  - Migration approach: Convert InSpec tests to Ansible assert tasks or Molecule verify steps.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Document count of credentials detected per module:
    - chef-automate-deployment: 1 password
    - chef-server-deployment: 1 password

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks will require careful mapping of test assertions.
  - Mitigation strategy: Create a mapping document for InSpec resources to Ansible assert statements or Molecule verify steps.

- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be converted to Ansible roles.
  - Mitigation strategy: Create an Ansible role that performs the same steps as the bash scripts, using Ansible modules for idempotency.

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already in Ansible format)
2. **InSpec tests** (moderate complexity, requires conversion to Ansible testing framework)
3. **Chef deployment scripts** (high complexity, requires complete rewrite as Ansible roles)

### Assumptions

1. The primary goal is to migrate all components to pure Ansible without any Chef dependencies.
2. The InSpec tests are used for compliance validation and need to be preserved in some form.
3. The deployment scripts for Chef Automate and Chef Infra Server will be replaced with equivalent Ansible roles for deploying alternative solutions.
4. The target environment will remain Ubuntu 20.04 or compatible Linux distributions.
5. The SSL/TLS security requirements will remain the same or be updated to current best practices.
6. The repository is primarily for demonstration purposes rather than production use, based on the README content.
7. No external data sources or complex integrations are present that would complicate migration.
8. The migration will preserve the same functionality but may improve implementation details where appropriate.