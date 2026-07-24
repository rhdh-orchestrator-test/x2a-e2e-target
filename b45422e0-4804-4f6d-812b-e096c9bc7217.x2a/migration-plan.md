# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and infrastructure configuration. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef server deployment scripts to Ansible playbooks

The complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration. The repository appears to be primarily educational/demonstration in nature rather than a production infrastructure codebase.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling older SSL protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH root login security compliance
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-lint for static analysis
  - Option 2: Use Molecule for Ansible role testing
  - Option 3: Maintain InSpec as a standalone testing tool that works with Ansible

- **Test Kitchen (latest)**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Simple Ansible playbook with assert modules for verification

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: Ansible AWX/Tower for orchestration
  - Option 2: GitLab CI/CD or other CI/CD platform for automation

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve:
  - TLS protocol version restrictions (currently TLS 1.2 only)
  - Certificate generation and management
  - Virtual host SSL configuration

- **SSH Hardening**: InSpec tests verify SSH root login is disabled. Migration should:
  - Maintain SSH security testing
  - Consider implementing actual SSH hardening in Ansible playbooks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks:
  - Challenge: InSpec has a domain-specific language for compliance testing
  - Mitigation: Use Ansible assert modules or maintain InSpec as a standalone tool

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible:
  - Challenge: The scripts use Chef-specific CLI tools
  - Mitigation: Research Ansible modules for package installation and use command/shell modules for Chef-specific commands if needed

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
   - Review and optimize existing Ansible playbook
   - Add documentation and improve variable naming

2. **poodle_fix.yml** (low risk, already in Ansible format)
   - Review and optimize existing Ansible playbook
   - Consider merging with website_https.yml as they relate to the same service

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible-compatible testing or maintain as standalone
   - Update test references in CI/CD pipelines

4. **Chef Server Deployment Scripts** (high complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement secret management with Ansible Vault

### Assumptions

1. The repository is primarily for demonstration/educational purposes rather than production use
2. The existing Ansible playbooks are functional and follow best practices
3. There is no complex Chef cookbook structure that needs migration
4. The InSpec tests are used for verification rather than remediation
5. The deployment scripts are used for setting up Chef infrastructure rather than being part of a larger Chef-managed environment