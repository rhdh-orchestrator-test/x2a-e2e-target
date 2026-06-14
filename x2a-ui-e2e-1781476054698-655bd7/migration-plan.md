# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The primary migration tasks will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks
3. Ensuring all compliance requirements are maintained during migration

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

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
    - Key Features: Disables SSLv3, enables TLSv1.2 only

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login testing

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used for testing the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts mention they can be used on "on-prem or cloud VM"

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible-native testing framework

- **Chef Automate/Infra Server**: Consider if these components are still needed or if they can be replaced with:
  - Ansible AWX/Tower for orchestration
  - Ansible Content Collections for compliance profiles

### Security Considerations

- **SSL/TLS Configuration**: The current implementation enforces TLSv1.2 and disables SSLv3 to mitigate POODLE vulnerability. This security practice must be maintained in the migrated solution.

- **SSH Security**: The InSpec tests verify that SSH root login is disabled. This compliance check must be preserved in the migrated solution.

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password)
  - Self-signed SSL certificates generated during deployment
  - Count: 2 credential sets detected (user login, SSL certificates)

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to Ansible-native testing solutions while maintaining the same level of compliance verification will require careful mapping of test capabilities.
  - Mitigation: Create a test mapping document that ensures each InSpec control has an equivalent Ansible test.

- **Chef Deployment Automation**: The Chef deployment scripts contain specific configurations that need to be translated to Ansible playbooks.
  - Mitigation: Create Ansible roles for Chef server deployment if Chef is still required in the environment, or replace with equivalent Ansible functionality.

### Migration Order

1. **website_https playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Add documentation and improve variable naming

2. **poodle_fix playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Consider merging with website_https playbook as they are related

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible-native testing solutions
   - Ensure all compliance checks are preserved

4. **Chef deployment scripts** (high complexity)
   - Convert to Ansible playbooks
   - Implement proper secret management for credentials

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance testing.
2. The Chef Automate and Chef Infra Server deployment scripts are still needed and should be converted to Ansible rather than eliminated.
3. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs.
4. The security requirements (TLSv1.2, disabled SSH root login) must be maintained.
5. No external dependencies or integrations beyond what's visible in the repository need to be considered.
6. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need functional changes.