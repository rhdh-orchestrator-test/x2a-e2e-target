# MIGRATION FROM CHEF/ANSIBLE HYBRID TO ANSIBLE

## Executive Summary

This repository contains a hybrid environment with both Chef and Ansible components, primarily focused on demonstrating Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec test profiles to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling older SSL protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration compliance testing

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS configuration and TLS protocols
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: HTTPS connectivity testing, TLS protocol verification

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/index.html`: Static HTML file, can be directly incorporated into Ansible content.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Lint for static analysis
  - Option 2: Use Molecule for integration testing
  - Option 3: Convert InSpec tests to equivalent Ansible assert tasks

- **Test Kitchen (latest)**: Replace with Molecule for Ansible role/playbook testing

- **Chef Automate/Infra Server**: If compliance reporting is needed, consider:
  - Option 1: Ansible AWX/Tower with compliance plugins
  - Option 2: Standalone compliance tools like OpenSCAP

### Security Considerations

- **SSL/TLS Configuration**: The playbooks handle SSL certificate generation and TLS protocol configuration. Migration should preserve:
  - Self-signed certificate generation
  - TLS 1.2 enforcement
  - Disabling of vulnerable protocols

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. Migration should:
  - Convert InSpec tests to Ansible assertions or molecule tests
  - Ensure SSH hardening is applied consistently

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Recommend migrating to Ansible Vault for credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing requires:
  - Understanding the InSpec resource model (port, http, ssl, sshd_config)
  - Creating equivalent Ansible assertions or molecule tests
  - Solution: Create a mapping of InSpec resources to Ansible modules/assertions

- **Compliance Reporting**: If compliance reporting is needed:
  - Challenge: Chef Automate provides built-in compliance reporting
  - Solution: Integrate Ansible with compliance tools like OpenSCAP or use AWX/Tower

### Migration Order

1. **website_https.yml** (already in Ansible format, low risk)
2. **poodle_fix.yml** (already in Ansible format, low risk)
3. **InSpec Tests** (convert to Ansible assertions or molecule tests, moderate complexity)
4. **Chef Automate/Server Deployment** (replace with Ansible AWX/Tower or alternative compliance solution, high complexity)

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are used for validation only and not for continuous compliance monitoring
3. There is no dependency on Chef-specific features beyond what's visible in the repository
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The deployment scripts for Chef Automate/Server may not need direct migration if the compliance functionality is replaced with an alternative solution