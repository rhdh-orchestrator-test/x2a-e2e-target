# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for continuous compliance validation. The repository also includes scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the content is already in Ansible format. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Adapting the Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
3. Ensuring the integration between the components is maintained

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to address POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **deploy-automate**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **deploy-chef-server**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Static HTML content for the web server. Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Simple Vagrant or Docker-based testing orchestrated by Ansible

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for enterprise automation platform
  - Option 2: Ansible Automation Platform
  - Option 3: GitLab CI/CD with Ansible for a CI/CD-based approach

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. This needs to be maintained with current best practices in the Ansible migration.
  - Migration approach: Use the same OpenSSL modules in Ansible, but update to latest security recommendations.

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Convert InSpec tests to Ansible assert statements or Molecule tests to verify the same security controls.

- **Credentials Management**: The deployment scripts contain hardcoded credentials.
  - Migration approach: Use Ansible Vault for secure credential storage.

- **Vault/secrets management**:
  - Hardcoded credentials in the deployment scripts (username, password)
  - SSL certificate generation and management
  - Count: 2 credential sets identified (user login, SSL certificates)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach.
  - Mitigation: Use Ansible's assert module with carefully crafted conditions that match InSpec's intent.

- **Chef Server Deployment**: Replacing Chef Server deployment with an Ansible-based solution.
  - Mitigation: Evaluate if Chef Server is still needed or if it can be fully replaced by Ansible Tower/AWX.

- **Integration Testing**: Ensuring that the compliance testing still works effectively after migration.
  - Mitigation: Create comprehensive integration tests that verify the same functionality as the original InSpec tests.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert these to Ansible-native testing solutions.
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert these to Ansible playbooks.

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used with Ansible for compliance automation, not to provide production-ready infrastructure code.
2. The deployment scripts are examples and not used in production environments (they contain hardcoded credentials).
3. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file.
4. The repository is intended for educational/demonstration purposes rather than production use.
5. The integration between Chef InSpec and Ansible is a key feature that needs to be preserved or replaced with equivalent functionality.
6. The security controls being tested (HTTPS configuration, SSH settings) are still relevant and should be maintained in the migration.