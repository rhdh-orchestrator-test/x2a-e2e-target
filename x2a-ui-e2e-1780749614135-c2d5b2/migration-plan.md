# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
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
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled (security compliance)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing web server functionality. Can be directly used in Ansible playbooks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis and best practices

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Set system parameters (vm.max_map_count, vm.dirty_expire_centisecs)
  - Download and install required packages
  - Configure users and organizations

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook:
  - Ensure TLSv1.2 is enabled and older protocols are disabled
  - Maintain proper certificate generation and configuration

- **SSH Security**: The SSH root login compliance check must be preserved:
  - Convert the InSpec control to an equivalent Ansible check
  - Consider implementing as an Ansible role that both configures and verifies SSH settings

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Compliance Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of InSpec resources to Ansible modules:
  - Challenge: InSpec provides domain-specific language for compliance testing that may not have direct equivalents in Ansible
  - Mitigation: Use a combination of Ansible modules (uri, command, assert) to replicate InSpec functionality

- **Test Framework Integration**: Ensuring that the testing framework integrates well with CI/CD pipelines:
  - Challenge: Test Kitchen has established integration with CI/CD tools
  - Mitigation: Document Molecule integration with the same CI/CD tools

### Migration Order

1. **website_https.yml** (already in Ansible, low risk)
2. **poodle_fix.yml** (already in Ansible, low risk)
3. **InSpec Tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef Deployment Scripts** (high complexity, requires complete rewrite as Ansible playbooks)

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance testing
2. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
3. There are no external dependencies or integrations not visible in the provided files
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only
5. The deployment scripts are intended for development/testing environments, not production
6. The compliance tests are based on specific security standards (STIG) that must be maintained
7. The current setup is used for demonstration/educational purposes rather than production workloads