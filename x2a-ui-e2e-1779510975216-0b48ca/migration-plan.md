# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing rather than being a pure Chef cookbook repository. Additionally, there are Chef Automate and Chef Infra Server setup scripts that need to be migrated to Ansible.

The migration scope is relatively small, with only a few files to migrate. The estimated timeline for this migration would be 1-2 weeks, with low complexity since most of the content is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already)
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already)
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-setup**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: System configuration, Chef Automate deployment, user and organization creation

- **chef-server-setup**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: System configuration, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Will need to be converted to Ansible-compatible test format.
- `tests/ssh_profile.rb`: InSpec test for SSH security compliance. Will need to be converted to Ansible-compatible test format.
- `index.html`: Sample HTML file used in the website deployment. Can be used as-is in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider maintaining InSpec as a separate testing tool if its capabilities are required

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the same security settings are maintained in the migrated Ansible playbooks.
  - Migration approach: The SSL configuration is already in Ansible format in website_https.yml and poodle_fix.yml.

- **SSH Security**: The InSpec tests check for SSH root login being disabled.
  - Migration approach: Create equivalent Ansible tasks to verify SSH configuration compliance.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated during playbook execution, no pre-existing secrets detected
  - Count of credentials per module:
    - chef-automate-setup: 3 (username, email, password)
    - chef-server-setup: 3 (username, email, password)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible formats may require additional tools or custom solutions.
  - Mitigation strategy: Consider using Ansible's assert module for basic tests, or maintain InSpec as a separate testing tool if its specific capabilities are required.

- **Chef Automate/Server Deployment**: The Chef Automate and Chef Infra Server deployment scripts need to be converted to Ansible playbooks.
  - Mitigation strategy: Create Ansible roles for Chef Automate and Chef Infra Server deployment, using the existing scripts as a reference for the required steps.

### Migration Order

1. **website_https and poodle_fix playbooks** (low risk, already in Ansible format)
   - Review and update as needed to follow Ansible best practices
   - Convert to Ansible roles if appropriate

2. **InSpec tests** (moderate complexity)
   - Convert to Ansible-compatible testing format
   - Integrate with the existing playbooks

3. **Chef Automate/Server deployment scripts** (high complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The primary goal is to migrate all components to pure Ansible, including replacing InSpec tests with Ansible-native testing solutions.
2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are functional and don't require significant changes.
3. The target environment will continue to be Ubuntu 20.04 or compatible systems.
4. There may be a need to maintain Chef Automate and Chef Infra Server in the environment, even after migrating the deployment scripts to Ansible.
5. The hardcoded credentials in the setup scripts are for demonstration purposes and will be replaced with proper secret management in the migrated solution.
6. The repository is primarily for demonstration purposes rather than production use, as indicated by the README.md mentioning it's companion material to a white paper.