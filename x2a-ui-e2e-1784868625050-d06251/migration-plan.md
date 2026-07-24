# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together for compliance automation. The repository appears to be a demonstration of how Chef InSpec can be used alongside Ansible for compliance testing rather than a full infrastructure-as-code implementation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while maintaining the existing Ansible playbooks.

**Timeline Estimate**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium
**Primary Focus**: Converting InSpec tests to Ansible-native testing solutions

## Module Migration Plan

This repository contains a hybrid Chef/Ansible setup that needs individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables only TLSv1.2

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance checking

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS is properly configured
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Will need to be updated to use Ansible-native testing.
- `chef-and-ansible/index.html`: Simple HTML file used as a test page for the web server.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - **Option 1**: Molecule with Testinfra for infrastructure testing
  - **Option 2**: Ansible Test for compliance validation
  - **Option 3**: Convert InSpec tests to Ansible assert tasks

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Server**: The deployment scripts suggest this environment was used for compliance reporting. Consider:
  - Migrating to Ansible Automation Platform for centralized management
  - Using AWX/Tower for reporting and compliance dashboards
  - Implementing alternative compliance reporting tools like OpenSCAP

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure the migration maintains:
  - TLSv1.2 protocol enforcement (from poodle_fix.yml)
  - Self-signed certificate generation (using Ansible's openssl modules)

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. Ensure:
  - Equivalent tests are created in the Ansible testing framework
  - SSH hardening is properly implemented in Ansible roles

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - No other credentials were detected in the repository

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks will require:
  - Understanding the InSpec resource models (port, http, ssl, sshd_config)
  - Creating equivalent assertions in Ansible-native testing tools
  - Ensuring compliance reporting capabilities are maintained

- **Test Kitchen to Molecule**: Migrating the test workflow will require:
  - Creating equivalent Molecule scenarios
  - Configuring Molecule to use the same Vagrant driver
  - Setting up appropriate verifiers for the tests

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - website_https.yml
   - poodle_fix.yml

2. **Testing Framework** (Medium complexity)
   - Convert InSpec tests to Ansible-native testing
   - Replace Test Kitchen with Molecule

3. **Chef Automate/Server Deployment** (High complexity)
   - Replace Chef Automate/Server deployment scripts with Ansible roles
   - Set up alternative compliance reporting solution

### Assumptions

1. The repository is primarily a demonstration of how Chef InSpec can work with Ansible rather than a production infrastructure-as-code implementation.

2. The main goal is to show compliance automation using InSpec alongside Ansible, as indicated by the README.md in the chef-and-ansible directory.

3. The setup-automate scripts are used to deploy a Chef environment for compliance reporting and are not part of the actual infrastructure configuration.

4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the actual deployment could be on any cloud or on-premises environment.

5. There is no complex data structure or variable management in the current implementation.

6. The repository does not contain actual secrets or sensitive data, but the setup-automate scripts have hardcoded credentials that would need to be properly managed in a production environment.

7. The migration will focus on maintaining the same functionality while moving completely to Ansible-native solutions.