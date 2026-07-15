# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

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
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file used as a test page for the web server

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
  - Molecule provides similar functionality but is designed specifically for Ansible

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks
  - Consider migrating to Ansible Tower/AWX for similar enterprise functionality

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Consider updating to also include TLSv1.3 support

- **SSH Security**: Maintain the SSH security controls verified by the InSpec test
  - Implement equivalent checks using Ansible's assert module or Molecule

- **Credentials Management**: 
  - The deployment scripts contain hardcoded credentials that should be moved to Ansible Vault
  - Count: 2 sets of credentials (username/password) in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests
  - Mitigation: Create custom Ansible modules or use the assert module with appropriate conditions
  - Example: Port checks can use the Ansible wait_for module, HTTP checks can use uri module

- **Compliance Metadata**: InSpec tests contain rich compliance metadata (STIG IDs, CCI references)
  - Mitigation: Store compliance metadata in Ansible variables or as comments in playbooks
  - Consider using Ansible tags to categorize controls by compliance framework

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **Chef deployment scripts** (moderate complexity, convert bash to Ansible)
4. **InSpec tests** (high complexity, requires testing framework decisions)

### Assumptions

1. The current setup uses Chef InSpec primarily for testing, not for configuration management
2. The target environment will continue to be Ubuntu 20.04 or compatible
3. Vagrant will continue to be used for development/testing environments
4. The security requirements (SSL/TLS versions, SSH configuration) will remain the same
5. There is no requirement to maintain backward compatibility with Chef InSpec
6. The deployment scripts are used for setting up test environments, not production systems
7. No external data sources or databases are referenced in the current configuration
8. No complex orchestration or multi-server dependencies exist in the current setup