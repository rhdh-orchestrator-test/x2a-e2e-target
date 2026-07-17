# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, primarily involving:

1. Chef InSpec test profiles that need to be migrated to Ansible-compatible testing frameworks
2. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
3. Existing Ansible playbooks that need to be reviewed and potentially refactored

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components and the fact that some components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing of a secure web server
    - Path: chef-and-ansible
    - Technology: Ansible playbooks with Chef InSpec tests
    - Key Features: HTTPS configuration, SSL/TLS security settings, Apache web server deployment

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible integration testing with InSpec verification. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure web server. Can be retained with minor refactoring to follow current Ansible best practices.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for addressing SSL POODLE vulnerability. Can be retained with minor refactoring.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs to be converted to an Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs to be converted to an Ansible playbook.

### Target Details

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml configuration)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for simple tests
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for playbook storage
  - Consider Ansible Semaphore as a lightweight alternative

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with SSL/TLS. Ensure the migrated Ansible playbooks maintain or improve upon the security settings:
  - Self-signed certificates are generated in the current playbook
  - TLS 1.2 is enforced, with older protocols disabled
  - Migration should consider updating to include TLS 1.3 support

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions. Ensure this security check is maintained in the migrated solution.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificate generation should use Ansible Vault for storing private keys

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible assertions or Molecule tests will require careful mapping of test logic.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions

- **Chef Automate Replacement**: Determining the right Ansible-based replacement for Chef Automate functionality.
  - Mitigation: Conduct a feature comparison between Chef Automate and Ansible AWX/Tower to ensure all required capabilities are covered

### Migration Order

1. **Existing Ansible Playbooks** (Low risk, high value)
   - Refactor `website_https.yml` and `poodle_fix.yml` to follow current Ansible best practices
   - Move hardcoded values to variables and templates
   - Implement idempotency improvements where needed

2. **InSpec Tests** (Moderate complexity)
   - Convert `website_https_verify.rb` and `ssh_profile.rb` to equivalent Ansible tests
   - Implement using Molecule or Ansible assertions

3. **Chef Deployment Scripts** (High complexity)
   - Convert `deploy-automate.sh` and `deploy-chef-server.sh` to Ansible playbooks
   - Implement secure credential management using Ansible Vault

### Assumptions

1. The primary goal is to eliminate Chef dependencies while maintaining equivalent functionality
2. Security compliance testing is a key requirement that must be preserved in the migration
3. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
4. Vagrant will continue to be used for development/testing environments
5. Self-signed certificates are acceptable for the web server configuration
6. The current level of parameterization (variables at the top of scripts) should be maintained or improved
7. No external data sources or APIs are being used that would require special handling
8. The migration does not need to include a Chef-to-Ansible converter tool, but rather a manual conversion process