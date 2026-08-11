# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be on showing how Chef InSpec can be used alongside Ansible for compliance testing, rather than being a full-fledged infrastructure management repository. There are also setup scripts for Chef Automate and Chef Infra Server deployment.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting the Chef InSpec tests to Ansible-native testing solutions
2. Replacing the Chef Automate/Infra Server setup scripts with Ansible playbooks
3. Ensuring the existing Ansible playbooks follow best practices

Given the limited scope, this migration could be completed in approximately 1-2 weeks by a single engineer familiar with both Chef and Ansible technologies.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables only TLSv1.2

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Compliance testing for SSH configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS is properly configured
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests port 443 listening, HTTPS response, and SSL/TLS protocol configuration

- **deploy-automate**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **deploy-chef-server**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Will need to be updated to use Ansible-native testing solutions.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions such as:
  - Molecule for Ansible role testing
  - ansible-lint for static code analysis
  - ansible-test for integration testing
  - Consider using Ansible's assert module for in-playbook validation

- **Test Kitchen**: Replace with Molecule for testing Ansible roles and playbooks

- **Chef Automate/Infra Server**: Replace with Ansible automation controller (AWX/Tower) for centralized management and compliance reporting

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with SSL/TLS. Ensure the migration maintains or improves the security posture by:
  - Using modern TLS protocols (TLS 1.2+)
  - Implementing proper cipher suites
  - Generating strong certificates

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. Ensure this security check is maintained in the Ansible solution.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook; consider using Ansible Vault for storing private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require understanding the compliance requirements and implementing equivalent checks using Ansible's testing tools.
  - Mitigation: Use Ansible's assert module for basic compliance checks and consider integrating with tools like OpenSCAP for more comprehensive compliance testing.

- **Chef Automate Replacement**: Finding an equivalent solution for Chef Automate's compliance reporting in the Ansible ecosystem.
  - Mitigation: Consider using AWX/Tower with custom reporting dashboards or integrating with third-party compliance tools.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format. Review and refactor to follow Ansible best practices.
2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Convert to Ansible-native testing solutions.
3. **Setup Scripts** (deploy-automate.sh, deploy-chef-server.sh): Create equivalent Ansible playbooks for deploying automation controller.
4. **Infrastructure Files** (kitchen.yml): Replace with Molecule configuration.

### Assumptions

1. The primary goal is to move all functionality to Ansible-native solutions, eliminating dependencies on Chef products.
2. The existing Ansible playbooks are functional but may need refactoring to follow best practices.
3. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs.
4. The compliance testing requirements will remain the same, just implemented with different tools.
5. There is no requirement to maintain backward compatibility with Chef InSpec or Chef Automate.
6. The hardcoded credentials in the setup scripts are for demonstration purposes only and will be replaced with secure credential management in the migrated solution.