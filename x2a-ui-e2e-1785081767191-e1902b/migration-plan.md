# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for demonstration purposes, along with Chef Automate and Chef Infra Server setup scripts. The migration scope is relatively small, focusing on standardizing all automation to Ansible while preserving the compliance testing capabilities currently provided by Chef InSpec.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains minimal code with clear functionality

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL/TLS vulnerabilities (POODLE) by enforcing TLSv1.2 protocol
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration compliance testing

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL/TLS protocol verification

- **chef-automate-setup**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-setup**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Simple HTML file used for testing web server functionality

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Convert InSpec tests to Ansible assert modules
  - Option 2: Use Ansible's integration with Molecule for testing
  - Option 3: Maintain InSpec tests but execute them via Ansible

- **Test Kitchen**: Replace with Ansible-native testing frameworks:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Simple Vagrant or Docker-based testing orchestrated by Ansible

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Option 1: Ansible Tower/AWX for web UI, job scheduling, and inventory management
  - Option 2: Ansible Semaphore for lightweight UI
  - Option 3: GitLab CI/CD for pipeline-based automation

### Security Considerations

- **SSL/TLS Configuration**: The current implementation enforces TLSv1.2 and disables older protocols. This security practice should be maintained in the Ansible migration.
  - Migration approach: Use the Ansible `lineinfile` or `replace` module similar to the existing implementation

- **SSH Hardening**: The InSpec test verifies that SSH root login is disabled.
  - Migration approach: Create an Ansible task to enforce this configuration and add an assert to verify compliance

- **Self-signed Certificates**: The current implementation generates self-signed certificates.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented in the existing playbook

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests requires understanding the compliance requirements and implementing equivalent checks.
  - Mitigation: Create a mapping document between InSpec resources and Ansible modules/assertions

- **Chef Automate Functionality**: If Chef Automate is being used for compliance reporting, an equivalent solution in the Ansible ecosystem will be needed.
  - Mitigation: Evaluate Ansible Tower/AWX compliance reporting capabilities or integrate with third-party compliance tools

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (already Ansible playbooks, low risk)
2. **InSpec Tests** (convert to Ansible assertions or Molecule tests, moderate complexity)
3. **Chef Automate/Server Setup Scripts** (convert to Ansible roles for infrastructure setup, higher complexity)

### Assumptions

1. The repository appears to be a demonstration/example repository rather than production code, based on the README content and simple examples.
2. The Chef InSpec tests are used for validation only and not part of a larger compliance reporting framework.
3. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with proper secret management in production.
4. The Test Kitchen configuration is used for local testing and demonstration, not for CI/CD pipelines.
5. There is no indication of external dependencies or integration with other systems beyond what's explicitly in the code.
6. The Apache configuration is relatively simple and doesn't include complex customizations that might be challenging to migrate.