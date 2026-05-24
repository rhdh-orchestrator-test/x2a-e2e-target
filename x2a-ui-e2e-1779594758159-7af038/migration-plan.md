# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. There are also Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, as most of the Ansible components are already in place. The estimated timeline for full migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS website functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTP response validation, SSL protocol verification, SSH configuration compliance

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts using Chef CLI tools
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing web server deployment. Can be reused as-is in Ansible.

### Target Details

Based on the source repository:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider migrating to ansible-test

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL protocols are maintained during migration.
  - Migration approach: Preserve the SSL protocol restrictions (TLSv1.2) in the Ansible tasks
  
- **SSH Security**: InSpec tests verify SSH root login is disabled. Ensure this compliance check is maintained.
  - Migration approach: Convert InSpec test to Ansible assert or Molecule verify step

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed certificates generated during deployment
  - Migration approach: Replace hardcoded credentials with Ansible Vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks may require additional tooling or custom modules.
  - Mitigation: Consider using Ansible's assert module for basic tests and Molecule for more complex verification.

- **Chef Server Deployment**: The Chef server deployment scripts need to be converted to Ansible playbooks.
  - Mitigation: Create Ansible roles for Chef server deployment if still needed, or consider replacing with Ansible AWX/Tower for similar functionality.

### Migration Order

1. **website_https.yml** (already in Ansible format, low risk)
2. **poodle_fix.yml** (already in Ansible format, low risk)
3. **InSpec Tests** (moderate complexity, convert to Ansible testing framework)
4. **Chef Deployment Scripts** (high complexity, convert to Ansible playbooks or replace functionality)

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can work alongside Ansible for compliance testing.
2. The Chef deployment scripts are used for setting up a test environment and are not part of the core functionality.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs.
4. No external dependencies or complex Chef cookbooks are present in this repository.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
6. The repository is primarily used for educational/demonstration purposes rather than production deployments.
7. The InSpec tests are the main Chef components that need migration to Ansible-native solutions.