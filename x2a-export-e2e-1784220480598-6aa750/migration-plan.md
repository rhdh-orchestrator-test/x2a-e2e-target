# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Replacing Chef Automate/Infra Server deployment scripts with Ansible playbooks

Estimated timeline: 1-2 weeks for a complete migration, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
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
    - Description: Chef InSpec control that verifies SSH root login is disabled (security compliance check)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance with specific tags (STIG, CCI)

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

- **automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file used as a test page for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider using the Ansible `community.general.inspec` module to continue using InSpec tests

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Or continue using Test Kitchen with the `kitchen-ansible` plugin

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enabled and older protocols remain disabled
  - Consider updating to also include TLSv1.3 support

- **SSH Security**: The SSH root login compliance check must be maintained
  - Convert the InSpec control to an Ansible task or assert

- **Vault/secrets management**:
  - Hardcoded credentials in the deployment scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests
  - Mitigation: Use the `community.general.inspec` module as an interim solution while gradually migrating tests

- **Chef Server Deployment**: Replacing Chef Server/Automate deployment scripts with Ansible
  - Mitigation: Create Ansible roles for Chef Server deployment or consider if Chef Server is still needed after migration

### Migration Order

1. **website_https.yml** (already Ansible, no migration needed)
2. **poodle_fix.yml** (already Ansible, no migration needed)
3. **InSpec Tests** (convert to Ansible testing framework)
4. **Deployment Scripts** (convert to Ansible playbooks)

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used with Ansible for compliance testing, not to provide production-ready infrastructure code.

2. The deployment scripts for Chef Automate and Chef Infra Server may not be needed after migration if the goal is to use Ansible exclusively.

3. The hardcoded credentials in the deployment scripts are for demonstration purposes only and would be replaced with secure credential management in a production environment.

4. The Test Kitchen configuration is used for development and testing, not for production deployments.

5. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the actual deployment could be on any compatible system.

6. The InSpec tests are focused on compliance checking rather than functional testing of the infrastructure.

7. There may be additional Chef components or dependencies not visible in the provided files that would need to be addressed during migration.