# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration tasks will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks

Estimated timeline: 1-2 weeks for a complete migration, with minimal complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enables TLSv1.2 only

- **inspec_website_test**:
    - Description: Chef InSpec test for verifying HTTPS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTP response testing, SSL protocol verification

- **inspec_ssh_test**:
    - Description: Chef InSpec test for SSH security settings
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration testing, root login verification, compliance with security requirements

- **chef_automate_deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef_server_deployment**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment example
- `chef-and-ansible/README.md`: Documentation file explaining the purpose of the examples
- `README.md`: Main repository documentation

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts could be used in any cloud environment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with Ansible's built-in `assert` module
  - Consider using Molecule for testing Ansible roles
  - For complex compliance testing, evaluate using OpenSCAP with Ansible

- **Test Kitchen with Vagrant**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in testing capabilities

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security improvements in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and SSLv3 is disabled
  - Maintain proper certificate generation and management

- **SSH Security**: The SSH profile tests security configurations that must be preserved
  - Ensure root login remains disabled
  - Maintain compliance with security requirements (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing style to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with appropriate conditionals to replicate InSpec tests
  - Consider using the `community.general.xml` module for parsing and validating configuration files

- **Chef Server Deployment**: Converting the Chef server deployment scripts to idempotent Ansible playbooks
  - Mitigation: Break down the shell scripts into discrete Ansible tasks
  - Use Ansible's package management modules instead of curl commands
  - Implement proper error handling and idempotence checks

### Migration Order

1. **website_https playbook** (already in Ansible, low risk)
   - Review and optimize the existing playbook
   - Add proper documentation and comments

2. **poodle_fix playbook** (already in Ansible, low risk)
   - Review and optimize the existing playbook
   - Add proper documentation and comments

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible assertions or Molecule tests
   - Ensure all compliance checks are maintained

4. **Chef deployment scripts** (high complexity)
   - Convert to Ansible playbooks
   - Implement proper secret management with Ansible Vault
   - Add idempotence and error handling

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance testing
2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need functional changes
3. The deployment scripts are currently used manually and not integrated into a larger automation system
4. No external dependencies or integrations beyond what's visible in the repository
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. The migration doesn't need to address scaling concerns as the examples appear to be for demonstration purposes
7. No database or complex application dependencies are present in the current implementation