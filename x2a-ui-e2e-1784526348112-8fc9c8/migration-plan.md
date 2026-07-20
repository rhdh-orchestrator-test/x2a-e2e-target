# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on two main components:

1. Chef Automate/Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec tests that need to be consolidated into a pure Ansible solution

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks, as the repository contains a limited number of scripts and playbooks with straightforward functionality.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure HTTPS website with Chef InSpec compliance testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security settings, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace this with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying an Apache web server with HTTPS. Can be retained but should be updated to follow current Ansible best practices.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Can be retained but should be updated to follow current Ansible best practices.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test for verifying HTTPS website functionality. Should be migrated to Ansible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec test for SSH security compliance. Should be migrated to Ansible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Should be converted to an Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Should be converted to an Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static code analysis and best practices enforcement

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Since the scripts are deploying Chef itself, the migration should focus on:
  - Creating Ansible playbooks to configure equivalent infrastructure monitoring and compliance solutions
  - Potentially integrating with AWX/Ansible Tower as a replacement for Chef Automate's UI and workflow capabilities

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. Migration should maintain or enhance these security settings.
  - Migration approach: Use Ansible's apache2_module and template modules to configure equivalent security settings

- **SSH Security**: InSpec tests verify SSH root login is disabled. Migration should include equivalent Ansible checks.
  - Migration approach: Use Ansible's lineinfile or template module to configure SSH and assert module to verify compliance

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates in the website_https.yml playbook should use Ansible Vault or a certificate management solution
  - Count of credentials detected: 3 (username, password, SSL certificate)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible's testing capabilities may require additional tooling or custom modules.
  - Mitigation: Use a combination of Ansible's assert module and custom scripts to achieve equivalent testing functionality.

- **Chef Automate Replacement**: If Chef Automate is being used for compliance reporting and visualization, finding an equivalent Ansible solution may be challenging.
  - Mitigation: Consider integrating with AWX/Ansible Tower and additional tools like Prometheus/Grafana for monitoring and reporting.

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/website_https.yml, chef-and-ansible/poodle_fix.yml)
   - Low risk as they're already in Ansible format
   - Update to follow current Ansible best practices
   - Replace hardcoded values with variables and Ansible Vault

2. **Testing Framework** (chef-and-ansible/tests/*)
   - Moderate complexity
   - Convert InSpec tests to Ansible assertions or Molecule tests
   - Update kitchen.yml to Molecule configuration

3. **Chef Deployment Scripts** (setup-automate/*)
   - Higher complexity
   - Convert Bash scripts to Ansible playbooks
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment, based on the README.md description.
2. The Chef InSpec tests are used for compliance verification of infrastructure deployed by Ansible, not for testing Chef cookbooks.
3. The setup-automate scripts are used to deploy Chef infrastructure, which will be replaced by Ansible infrastructure in the migration.
4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.
5. The migration will maintain the same level of security compliance currently verified by InSpec tests.
6. No external dependencies or integrations beyond what's visible in the repository need to be considered.
7. The hardcoded credentials in the setup scripts are for demonstration purposes and will be properly secured in the migrated solution.