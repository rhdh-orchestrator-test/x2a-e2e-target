# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the configuration is already in Ansible format. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Adapting the Chef Automate/Infra Server deployment scripts to Ansible playbooks
3. Ensuring the existing Ansible playbooks follow best practices

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled (security compliance check)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance with specific tags (STIG, CCI)

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used for testing web server configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment (based on comments in setup scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider using the Ansible `community.general.inspec` module to continue using InSpec tests

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Consider keeping Test Kitchen if the team is familiar with it, as it can work with Ansible

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or GitHub Actions for pipeline automation
  - Compliance automation can be handled by OpenSCAP or continued with InSpec via the Ansible module

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should:
  - Maintain the same security level or improve it
  - Consider using Ansible Vault for storing sensitive information
  - Implement certificate management using Ansible modules

- **SSH Security**: The InSpec test checks for SSH root login being disabled. Migration should:
  - Maintain this security check in the new testing framework
  - Ensure SSH hardening is part of the base configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely
  - Count of credentials detected: 3 (username, password, organization name in setup scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require:
  - Understanding the compliance requirements being tested
  - Finding equivalent Ansible modules or assertions
  - Maintaining the same level of reporting and documentation
  - Mitigation: Consider using the `community.general.inspec` module to continue using existing InSpec tests

- **Chef Automate Functionality**: Replacing Chef Automate's compliance dashboard and reporting:
  - Ansible AWX/Tower provides some reporting but may not have all the compliance features
  - Additional tools like OpenSCAP or Prometheus/Grafana may be needed
  - Mitigation: Evaluate if all Chef Automate features are actually being used before replacing them

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format; just need to be reviewed and optimized
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity; need to be converted to Ansible testing framework
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity; need to be converted to Ansible playbooks and integrated with secrets management

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are being used for compliance validation of Ansible-managed systems
3. The deployment scripts are used for setting up test environments rather than production systems
4. There are no external dependencies or integrations not visible in the repository
5. The hardcoded credentials in the setup scripts are for demonstration purposes only
6. The repository is not using any Chef cookbooks or recipes that would need migration
7. The target environment is Ubuntu 20.04 running on Vagrant VMs
8. There are no specific performance requirements for the migrated solution
9. The migration will maintain the same level of security compliance checking
10. The team has experience with both Chef InSpec and Ansible