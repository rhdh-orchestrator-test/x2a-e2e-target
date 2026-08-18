# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with shell scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, with a focus on converting existing Ansible playbooks to a more standardized Ansible structure and replacing Chef InSpec tests with Ansible-native testing solutions. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of playbooks and tests.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

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
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Simple HTML file used as a template for website deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For infrastructure testing: Use Ansible Molecule with testinfra or Ansible's assert module
  - For compliance testing: Consider using ansible-lint with custom rules or OpenSCAP integration

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks

- **Chef Automate/Infra Server**: Consider migrating to Ansible Tower/AWX for centralized management or using GitLab CI/GitHub Actions for pipeline-based automation

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Ensure proper SSL/TLS settings are maintained in the migrated Ansible roles.
  - Migration approach: Convert the SSL configuration to an Ansible role with configurable cipher suites and protocols

- **SSH Security**: The InSpec tests verify SSH security configurations. Implement equivalent checks in Ansible.
  - Migration approach: Create Ansible tasks to verify and enforce SSH security settings

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions will require understanding the equivalent assertions and checks.
  - Mitigation: Use Ansible's assert module or Molecule with testinfra for functional testing, and ansible-lint for compliance checks

- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be converted to Ansible playbooks.
  - Mitigation: Create Ansible roles for deploying alternative solutions like Ansible Tower/AWX or other CI/CD tools

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Convert to a proper Ansible role structure with variables
2. **poodle_fix.yml** (low risk, already Ansible): Integrate into the Apache/web server role
3. **InSpec Tests** (moderate complexity): Convert to Ansible-native testing solutions
4. **Chef Deployment Scripts** (high complexity): Create Ansible playbooks for alternative deployment solutions

### Assumptions

1. The repository is primarily used for demonstration purposes, as indicated by the README.md mentioning "working examples" and "how-tos".
2. The Ansible playbooks are designed to work with Ubuntu 20.04, and the migration will target the same OS version.
3. The Chef InSpec tests are used for compliance validation and can be replaced with equivalent Ansible-native testing solutions.
4. The deployment scripts for Chef Automate and Chef Infra Server will need to be replaced with equivalent functionality using Ansible or alternative tools.
5. No external dependencies or complex integrations exist beyond what is visible in the repository.
6. The migration will maintain the same functionality but using Ansible-native approaches throughout.
7. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migrated solution.