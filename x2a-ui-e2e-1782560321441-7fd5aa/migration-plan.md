# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The primary migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks
3. Ensuring all compliance requirements are maintained during migration

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **inspec_compliance_tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login testing

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible-native testing framework

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that:
  - Set system parameters (vm.max_map_count, vm.dirty_expire_centisecs)
  - Download and install required packages
  - Configure users and organizations

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Migration approach: Ensure the Ansible playbook continues to enforce the same SSL/TLS protocol restrictions

- **SSH Security**: The InSpec test checks for disabled root login via SSH
  - Migration approach: Create an Ansible task that ensures PermitRootLogin is not set to 'yes' in sshd_config

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions
  - Mitigation: Use Ansible's assert module for basic tests and consider Molecule for more complex testing scenarios

- **Maintaining Compliance**: Ensuring all security compliance checks are preserved during migration
  - Mitigation: Create a compliance matrix mapping InSpec controls to new Ansible checks

- **Chef Server Deployment**: Converting Chef server deployment scripts to idempotent Ansible playbooks
  - Mitigation: Use Ansible's idempotent modules (e.g., command with changed_when) to ensure clean runs

### Migration Order

1. **website_https playbook** (already in Ansible, low risk)
   - Review and optimize existing Ansible playbook
   - Add idempotency improvements if needed

2. **poodle_fix playbook** (already in Ansible, low risk)
   - Review and optimize existing Ansible playbook
   - Add idempotency improvements if needed

3. **InSpec compliance tests** (moderate complexity)
   - Convert to Ansible assert statements or Molecule tests
   - Ensure all compliance checks are maintained

4. **Chef deployment scripts** (high complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance testing
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need functional changes
3. The deployment scripts for Chef Automate/Infra Server need to be converted to Ansible to eliminate the dependency on Chef
4. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs
5. There are no external dependencies or integrations not visible in the provided repository
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure alternatives