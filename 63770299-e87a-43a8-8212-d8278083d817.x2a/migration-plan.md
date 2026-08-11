# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and infrastructure configuration. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate and Chef Infra Server deployment scripts to Ansible

Given the limited scope and the fact that part of the infrastructure is already using Ansible, this migration is estimated to be of low complexity and can likely be completed within 1-2 weeks by a single engineer familiar with both Chef and Ansible technologies.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH root login security compliance
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-test for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static code analysis
  - Option 4: For compliance testing specifically, consider migrating to OpenSCAP with Ansible

- **Test Kitchen (latest)**: Replace with:
  - Molecule for Ansible role and playbook testing
  - Consider keeping Test Kitchen if the team is familiar with it, as it can work with Ansible

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open-source version of Ansible Tower) for smaller deployments
  - GitLab CI/CD or GitHub Actions for pipeline-based automation

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the same level of security by:
  - Preserving the TLS 1.2 requirement and disabling older protocols
  - Ensuring proper certificate generation and management
  - Maintaining secure virtual host configurations

- **SSH Hardening**: Ensure the SSH security controls tested by InSpec are implemented in Ansible:
  - Disable root login via SSH
  - Implement the same CIS/STIG controls referenced in the InSpec tests

- **Vault/secrets management**:
  - Current implementation has hardcoded credentials in the Chef server deployment scripts
  - Migration should use Ansible Vault to secure sensitive information like:
    - User passwords (currently hardcoded as 'password')
    - Organization credentials
    - SSL private keys

### Technical Challenges

- **Test Framework Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks:
  - InSpec has a different testing paradigm than Ansible's verification modules
  - Solution: Use Ansible assert modules or integrate with Molecule for testing

- **Certificate Management**: Ensuring proper SSL certificate generation and management:
  - Current implementation uses OpenSSL modules in Ansible
  - Solution: Continue using Ansible's crypto modules but implement better secret management

- **Chef Server Deployment**: Replacing Chef server deployment scripts:
  - Current implementation uses bash scripts to deploy Chef infrastructure
  - Solution: Create Ansible roles for infrastructure management platforms

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml):
   - Low risk as they're already in Ansible format
   - Refactor to use roles and improve variable management
   - Implement Ansible Vault for any sensitive data

2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb):
   - Convert to Ansible-compatible testing frameworks
   - Integrate with CI/CD pipeline for automated testing

3. **Chef Server Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh):
   - Highest complexity due to the need to replace Chef-specific functionality
   - Create Ansible roles for deploying alternative infrastructure management platforms

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production, based on the README description mentioning "examples" and "companion to a white paper".

2. The Chef InSpec tests are used for compliance validation of infrastructure that could be managed by either Chef or Ansible.

3. The deployment scripts for Chef Automate and Chef Infra Server are intended for setting up a Chef environment, which would be replaced by an Ansible-based solution.

4. The target environment is Ubuntu 20.04 based on the Test Kitchen configuration, though the deployment scripts might work on other Linux distributions.

5. The security requirements include disabling SSH root login and enforcing TLS 1.2 for web services, which must be maintained in the Ansible migration.

6. There are no complex data transformations or Chef-specific resources that would require special handling during migration.

7. The team has experience with both Chef and Ansible, making the transition more straightforward.