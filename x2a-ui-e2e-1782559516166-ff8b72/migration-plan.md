# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also includes shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks

Estimated timeline: 1-2 weeks for a complete migration, with minimal complexity due to the limited scope of Chef components.

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

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality of the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks with STIG references

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing. Migration consideration: Can be kept as-is or managed as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider integrating with OpenSCAP for compliance testing

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Install and configure equivalent monitoring/compliance tools
  - Set up users and organizations in the new environment

### Security Considerations

- **SSL Configuration**: The migration must maintain the security improvements in the poodle_fix.yml playbook, ensuring TLSv1.2 is enforced.
- **SSH Security**: The SSH compliance checks in ssh_profile.rb need to be preserved in the Ansible-native testing solution.
- **Vault/secrets management**:
  - Hardcoded credentials in the deployment scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook and should be handled securely in the migrated solution
  - Count of credentials detected: 2 (username/password in deployment scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional logic and careful validation to ensure equivalent test coverage.
  - Mitigation: Consider using Ansible's assert module with well-defined conditions that match InSpec's expectations.

- **Compliance Reporting**: InSpec provides rich compliance reporting that may not be directly available in Ansible.
  - Mitigation: Integrate with tools like OpenSCAP or AWX/Tower for compliance reporting capabilities.

- **Chef Server Functionality**: If any Chef Server functionality is being used beyond what's in the deployment scripts, those features will need equivalent Ansible implementations.
  - Mitigation: Evaluate if AWX/Tower can provide the required functionality or if additional tools are needed.

### Migration Order

1. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing first to establish the compliance baseline.
2. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Create Ansible playbooks to replace these scripts.
3. **Test Kitchen Configuration**: Replace with Molecule after the tests have been migrated.

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production, as indicated by the README.md mentioning it's a companion to a white paper.
2. The Chef InSpec tests are used solely for validation and not for any runtime configuration management.
3. There are no additional Chef cookbooks or resources beyond what's visible in the repository.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and not used in production environments.
5. The Apache web server configuration is relatively simple and doesn't have complex dependencies.
6. The migration will maintain the same level of security compliance as demonstrated in the InSpec tests.
7. The target environment will continue to be Ubuntu 20.04 or compatible systems.