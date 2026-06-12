# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The migration will primarily involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Updating the deployment scripts to use Ansible instead of Bash
3. Ensuring all compliance checks are properly implemented in the new Ansible framework

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

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
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used as a test page. Can be directly used in Ansible without changes.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider using pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Consider alternatives:
  - Option 1: Ansible AWX/Tower for enterprise management
  - Option 2: GitLab CI/CD for pipeline management
  - Option 3: Jenkins with Ansible plugins

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enabled and older protocols disabled
  - Consider updating to also include TLSv1.3 support

- **SSH Security**: Maintain the SSH root login restrictions from the InSpec profile
  - Implement as Ansible tasks that configure sshd_config
  - Add idempotent checks to verify the configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  - Consider using ansible.builtin.assert or custom modules for complex validations

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated
  - Mitigation: Investigate integration with compliance tools like OpenSCAP or custom reporting solutions

- **Deployment Scripts**: Converting Bash deployment scripts to Ansible requires understanding of Chef Automate architecture
  - Mitigation: Create Ansible roles that replicate the Chef Automate deployment process or replace with AWX/Tower

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to a proper Ansible role structure

2. **poodle_fix playbook** (low risk, already Ansible)
   - Integrate into the website_https role as a security hardening task
   - Update to include more current security best practices

3. **InSpec tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests
   - Convert ssh_profile.rb to Ansible security role

4. **Deployment scripts** (high complexity)
   - Create Ansible playbooks to replace the Chef Automate and Chef Infra Server deployment scripts
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The primary goal is to standardize on Ansible and remove Chef dependencies
2. Compliance testing is a critical requirement that must be maintained
3. The deployment scripts are used for setting up test environments and not production systems
4. The current security configurations are appropriate and should be maintained
5. No custom Chef resources or complex Chef-specific logic is present that would require special handling
6. The target environment will continue to be Ubuntu 20.04 or compatible systems
7. Test Kitchen is only used for development/testing and not in production pipelines
8. No external data sources or integrations are present that would require special handling