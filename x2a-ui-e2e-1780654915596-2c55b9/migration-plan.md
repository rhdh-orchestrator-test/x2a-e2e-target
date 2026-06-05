# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate to a pure Ansible solution. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
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
    - Description: Chef InSpec control that ensures SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing. Migration consideration: Can be used as-is or templated in Ansible.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts suggest on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule with Testinfra for more comprehensive testing
  - Option 4: Consider OpenSCAP integration for compliance scanning

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain the same level of security in Apache configuration

- **SSH Security**: The SSH root login check must be preserved in the Ansible solution
  - Consider using Ansible's built-in security modules or OpenSCAP integration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using Ansible Vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test functionality
  - Challenge: InSpec has specific matchers and resources that may not have direct equivalents in Ansible
  - Mitigation: Use a combination of Ansible assert module, Testinfra, and custom modules where needed

- **Chef Automate/Server Deployment**: Replacing Chef infrastructure deployment with equivalent Ansible automation
  - Challenge: The Chef Automate/Server deployment scripts perform specific Chef-related configurations
  - Mitigation: If Chef infrastructure is still needed, Ansible can be used to automate the deployment scripts; if not, equivalent monitoring and compliance solutions managed by Ansible should be identified

### Migration Order

1. **website_https.yml** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Ensure idempotence and best practices

2. **poodle_fix.yml** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Consider merging with website_https.yml as they are related

3. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible/Molecule tests
   - Convert ssh_profile.rb to Ansible security checks

4. **Chef Deployment Scripts** (high complexity)
   - Determine if Chef infrastructure is still needed
   - If yes: Create Ansible playbooks to automate the deployment scripts
   - If no: Identify and implement alternative solutions with Ansible

### Assumptions

1. The primary goal is to migrate to a pure Ansible solution, eliminating the dependency on Chef InSpec for testing.
2. The target environment will continue to be Ubuntu 20.04 or compatible systems.
3. The Apache web server configuration requirements will remain the same.
4. The security requirements (TLSv1.2, SSH hardening) will remain in place.
5. It's unclear if Chef Automate/Server is still required or if it should be replaced with an alternative solution.
6. The repository appears to be primarily for demonstration/educational purposes rather than production use.
7. No specific performance requirements are mentioned that might affect the migration approach.
8. The existing Ansible playbooks follow a basic structure and may benefit from refactoring to use roles and collections.