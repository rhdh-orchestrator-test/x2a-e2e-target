# MIGRATION FROM CHEF/ANSIBLE HYBRID TO ANSIBLE

## Executive Summary

This repository contains a hybrid environment with both Chef InSpec tests and Ansible playbooks. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The repository also includes scripts for setting up Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The complexity is low to moderate, with the main challenge being preserving the compliance testing functionality currently provided by InSpec. Estimated timeline for migration is 1-2 weeks, including testing and validation.

## Module Migration Plan

This repository contains a hybrid Chef/Ansible environment that needs individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

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
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests port 443 listening, HTTPS response, SSL/TLS protocol security

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

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/index.html`: Simple HTML file, likely used as a template or example. Migration consideration: Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml as the driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with testinfra for infrastructure testing
  - Option 2: Use Ansible Molecule with Ansible's assert module for compliance checks
  - Option 3: Integrate with OpenSCAP or other compliance tools via Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure code

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open-source upstream of Ansible Tower) for smaller deployments
  - GitLab CI/CD or Jenkins for pipeline-based automation

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with SSL/TLS. Ensure the migration preserves the security hardening that disables vulnerable protocols (SSLv3) and enables only TLSv1.2.
  - Migration approach: Use the same configuration parameters in the Ansible apache2_module and template modules.

- **SSH Security**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Create equivalent tests using Ansible Molecule and testinfra, or implement as Ansible assert tasks.

- **Self-signed Certificates**: The current implementation generates self-signed certificates.
  - Migration approach: Consider upgrading to Let's Encrypt integration for production environments.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets detected in setup scripts

### Technical Challenges

- **Compliance Testing**: The primary challenge is replacing Chef InSpec's compliance testing capabilities.
  - Mitigation strategy: Evaluate Ansible Molecule with testinfra, which provides similar testing capabilities. Alternatively, consider integrating with OpenSCAP or maintaining InSpec as a standalone testing tool called from Ansible.

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate testing.
  - Mitigation strategy: Replace with Ansible Molecule, which is designed specifically for testing Ansible roles and playbooks.

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
   - Simply reorganize into Ansible roles for better maintainability
   - Update any deprecated syntax

2. **poodle_fix.yml** (low risk, already in Ansible format)
   - Integrate into the website_https role as a task
   - Update any deprecated syntax

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible Molecule tests with testinfra
   - Ensure all compliance checks are preserved

4. **Chef Automate/Server Setup Scripts** (high complexity)
   - Replace with Ansible playbooks for setting up Ansible Automation Platform or AWX
   - Implement user and organization management through Ansible

### Assumptions

1. The primary goal is to standardize on Ansible and eliminate Chef dependencies
2. Compliance testing is a critical requirement that must be preserved
3. The current setup is used for demonstration/testing rather than production
4. The self-signed certificates are acceptable for the environment (not production)
5. The hardcoded credentials in setup scripts are for demonstration purposes only
6. The target environment will continue to be Ubuntu 20.04 or compatible
7. Vagrant will continue to be used for local development/testing
8. The Apache configuration requirements will remain the same