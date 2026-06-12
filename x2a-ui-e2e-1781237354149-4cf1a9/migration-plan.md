# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that will need to be replaced with Ansible equivalents.

Estimated timeline: 1-2 weeks for a single developer, with minimal complexity due to the small codebase and clear separation of concerns.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-verification**:
    - Description: Chef InSpec test profile that validates HTTPS website deployment and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS content verification, SSL protocol validation

- **ssh-security-profile**:
    - Description: Chef InSpec test profile that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login validation, STIG compliance check

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used for testing web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
  - Molecule provides similar functionality but is designed specifically for Ansible

- **Chef Automate/Infra Server**: Replace with Ansible alternatives:
  - AWX/Ansible Tower for web UI and job scheduling
  - Ansible Semaphore for a lighter-weight alternative
  - Git repositories for playbook storage and version control

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains the minimum protocol version
  - Consider updating to include TLSv1.3 support

- **SSH Hardening**: The SSH security profile tests must be converted to Ansible checks
  - Create equivalent checks using Ansible's assert module or custom modules

- **Secrets Management**: 
  - The Chef deployment scripts contain hardcoded credentials that should be moved to Ansible Vault
  - Count: 1 password in each deployment script

- **Certificate Management**:
  - Self-signed certificates are generated in the playbook
  - Consider integrating with a certificate management solution or Let's Encrypt

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with carefully crafted conditions that match InSpec's intent
  - Consider using community.general.assert_that module for more readable assertions

- **Compliance Validation**: Maintaining compliance validation capabilities without InSpec
  - Mitigation: Evaluate OpenSCAP integration with Ansible for STIG compliance checks
  - Consider developing custom Ansible modules for specific compliance checks

- **Chef Automate Replacement**: Finding equivalent functionality in the Ansible ecosystem
  - Mitigation: Map Chef Automate features to AWX/Tower features
  - Develop custom reporting solutions for compliance data if needed

### Migration Order

1. **website-https and poodle-fix playbooks** (low risk, already in Ansible)
   - Review and update as needed
   - No migration required, but consider updating to use more modern Ansible practices

2. **InSpec test conversion** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions
   - Convert ssh_profile.rb to Ansible compliance checks

3. **Chef deployment scripts** (high complexity)
   - Create Ansible playbooks to replace the Chef Automate and Chef Server deployment scripts
   - Implement secure credential management with Ansible Vault

4. **Test Kitchen to Molecule** (moderate complexity)
   - Create molecule.yml configuration to replace kitchen.yml
   - Set up test scenarios that match the current Test Kitchen configuration

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than for production use
2. The hardcoded credentials in the deployment scripts are examples and not used in production
3. The target environment is Ubuntu 20.04 as specified in kitchen.yml
4. The SSH profile is intended for RHEL systems (based on the STIG references) but is being used on Ubuntu
5. The repository is used for educational/demonstration purposes based on the README content
6. No external dependencies or complex infrastructure are involved beyond what's visible in the repository
7. The migration will maintain the same level of security validation currently provided by InSpec
8. The team has experience with both Chef InSpec and Ansible