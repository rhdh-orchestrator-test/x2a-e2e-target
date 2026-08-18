# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and infrastructure configuration. The repository appears to be a demonstration or example repository showing how Chef InSpec can be used alongside Ansible for compliance testing. There are also scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The primary focus will be on:
1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Ensuring the Chef Automate/Infra Server deployment scripts are replaced with Ansible playbooks
3. Maintaining the compliance testing capabilities while fully migrating to Ansible

**Estimated Timeline**: 1-2 weeks for a complete migration, with minimal complexity due to the small codebase and existing Ansible components.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance testing

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration file for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/index.html`: Simple HTML file, likely used as a test page. No migration needed.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or any cloud environment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Configure system requirements (hostname, sysctl parameters)
  - Install and configure alternative compliance and infrastructure management tools

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (already addressed in poodle_fix.yml)
  - Consider adding more modern cipher suites
  - Implement proper certificate management

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Migration should:
  - Maintain this check in the new testing framework
  - Consider expanding SSH hardening measures

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **Testing Framework Transition**: Moving from InSpec to Ansible-native testing requires:
  - Understanding the equivalent assertions in Ansible
  - Ensuring the same level of compliance validation
  - Solution: Create a mapping of InSpec resources to Ansible modules/assertions

- **Maintaining Compliance Validation**: The repository demonstrates compliance automation:
  - Challenge: Ensuring the same level of compliance reporting and validation
  - Solution: Investigate Ansible-compatible compliance frameworks like OpenSCAP integration

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format. Review and update as needed.
2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Convert to Ansible-compatible testing framework.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Create equivalent Ansible playbooks.
4. **Test Kitchen Configuration**: Replace with Molecule for testing the Ansible playbooks.

### Assumptions

1. The repository is primarily for demonstration purposes, not production use
2. The hardcoded credentials in the deployment scripts are for demonstration only
3. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file
4. The compliance tests are meant to be run against systems configured by the Ansible playbooks
5. There is no complex data structure or state management required
6. The repository is not actively used in a CI/CD pipeline
7. There are no external dependencies or integrations beyond what's visible in the code
8. The self-signed certificates are acceptable for the demonstration environment