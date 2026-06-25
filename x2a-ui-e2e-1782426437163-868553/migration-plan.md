# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The primary migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks
3. Ensuring all compliance checks are preserved in the new implementation

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
    - Key Features: Disables SSLv3 and enables only TLSv1.2 for Apache

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-server-deployment**:
    - Description: Shell script to deploy Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef server installation, user and organization creation

- **automate-deployment**:
    - Description: Shell script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for testing web server functionality

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
  - Molecule provides similar functionality but is more Ansible-native

- **Chef Automate/Infra Server**: Replace with Ansible alternatives:
  - AWX/Ansible Tower for web UI and job scheduling
  - Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain the same level of security in Apache configuration

- **SSH Security**: The SSH root login check must be preserved
  - Convert the InSpec test to an Ansible task that verifies the same configuration
  - Consider implementing remediation in addition to checking

- **Credentials Management**: 
  - The deployment scripts contain hardcoded credentials that should be moved to Ansible Vault
  - Count: 2 credentials detected (username/password in deployment scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with appropriate conditionals to achieve similar validation
  - Consider custom Ansible modules for complex validations

- **Compliance Reporting**: InSpec provides structured compliance reporting that needs an equivalent in Ansible
  - Mitigation: Implement custom reporting using Ansible's callback plugins or integrate with AWX/Tower reporting

- **Test Kitchen to Molecule**: Ensuring test scenarios are properly migrated
  - Mitigation: Create equivalent Molecule scenarios that test the same functionality

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - No migration needed, just potential improvements

2. **poodle_fix.yml** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - No migration needed, just potential improvements

3. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions
   - Convert ssh_profile.rb to Ansible assertions
   - Implement equivalent reporting mechanism

4. **Deployment Scripts** (high complexity)
   - Convert deploy-chef-server.sh to Ansible playbook
   - Convert deploy-automate.sh to Ansible playbook
   - Implement Ansible Vault for credential storage

### Assumptions

1. The primary goal is to move entirely to Ansible and eliminate Chef dependencies
2. The InSpec tests are used for compliance validation and their functionality must be preserved
3. The deployment scripts are used for setting up Chef infrastructure which will be replaced by Ansible infrastructure
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Vagrant will continue to be used for development/testing environments
6. The security requirements (TLS configuration, SSH hardening) must be maintained
7. No external data sources or integrations are present beyond what's visible in the repository
8. The migration will include improving security practices (e.g., removing hardcoded credentials)