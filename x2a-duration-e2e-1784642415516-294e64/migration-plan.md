# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for continuous compliance validation. The repository also includes setup scripts for Chef Automate and Chef Infra Server deployment.

The migration scope is relatively small, as most of the content is already in Ansible format. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Updating the Chef Automate/Infra Server setup scripts to Ansible playbooks
3. Ensuring all compliance requirements are maintained during migration

Estimated timeline: 1-2 weeks for a complete migration, with minimal complexity due to the small codebase and existing Ansible components.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

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
    - Description: Chef InSpec profile that verifies SSH security compliance (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, CCI compliance checks, STIG validation

- **chef-automate-setup**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-setup**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Simple HTML file used as a test page for the web server setup.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks
  - Option 4: Consider using Ansible's built-in test modules (e.g., uri, stat, command with register)

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and control
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance scanning tools like OpenSCAP or DISA SCAP

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook, ensuring TLSv1.2 is enforced and older protocols are disabled.

- **SSH Hardening**: The SSH compliance checks in ssh_profile.rb must be converted to equivalent Ansible checks to ensure root login remains disabled.

- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider enhancing this with Let's Encrypt integration for production environments.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional logic and careful validation to ensure equivalent coverage.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules and develop reusable test playbooks.

- **Compliance Validation**: Ensuring that all compliance checks from InSpec are fully covered in the Ansible migration.
  - Mitigation: Create a compliance matrix to track each control and its implementation in Ansible.

- **Chef Server Functionality**: Replacing Chef Server functionality with Ansible Tower/AWX may require workflow adjustments.
  - Mitigation: Document the Chef Server workflows and map them to equivalent Ansible Tower/AWX workflows.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format. Only need minor updates to follow best practices and integrate with new testing framework.

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing solutions. Medium complexity due to the need to maintain equivalent compliance validation.

3. **Setup Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks for infrastructure setup. Higher complexity due to the need to replace Chef-specific functionality with Ansible equivalents.

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment solution.

2. The target environment is Ubuntu 20.04 as specified in kitchen.yml, though the setup scripts don't explicitly specify an OS.

3. The security compliance requirements (particularly in ssh_profile.rb) are based on specific standards (SRG-OS-000112, RHEL-08-000227) that must be maintained in the Ansible migration.

4. The repository is intended for educational/demonstration purposes rather than production use, given the simple examples and test-focused structure.

5. The migration to Ansible should maintain the same level of compliance validation currently provided by InSpec.

6. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with secure credential management in a production environment.