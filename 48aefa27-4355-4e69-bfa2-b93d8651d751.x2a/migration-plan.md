# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains examples of using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef server and Automate deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for deploying a secure Apache web server with SSL/TLS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test for verifying HTTPS website functionality
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL/TLS protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test for SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, STIG compliance checks

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

- **automate-deployment**:
    - Description: Bash script for deploying Chef Automate with Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server integration, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible and InSpec integration. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing web server deployment. Can be preserved as-is or incorporated into Ansible templates.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but deployment scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule with Testinfra for infrastructure testing
  - Option 2: Ansible Test for compliance testing
  - Option 3: Ansible Lint for static code analysis

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Server/Automate**: Replace deployment scripts with Ansible playbooks that configure equivalent functionality or alternative solutions:
  - AWX/Ansible Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance scanning with OpenSCAP or similar tools

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the secure TLS 1.2 configuration and disabled SSL3 protocol as implemented in the current playbooks.
  - Approach: Use Ansible's `openssl_*` modules as already implemented in the existing playbooks.

- **SSH Hardening**: The SSH security profile tests must be converted to equivalent Ansible checks.
  - Approach: Create Ansible tasks that enforce the same SSH configuration parameters.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault.
  - SSL certificates and keys should be managed securely, potentially using Ansible Vault or external secret management.
  - Count of credentials detected: 3 (username, password, and SSL key)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks may require different syntax and approaches.
  - Mitigation: Use Molecule with Testinfra which provides similar testing capabilities to InSpec.

- **Chef Server/Automate Replacement**: Determining the right Ansible-based alternatives for Chef Server and Automate functionality.
  - Mitigation: Evaluate AWX/Tower, GitLab CI/CD, or Jenkins as potential replacements based on specific requirements.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format and can be preserved with minimal changes.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible-native testing.
3. **Deployment Scripts** (deploy-chef-server.sh, deploy-automate.sh): High complexity as they require complete rewrite as Ansible playbooks and determination of replacement technologies.

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while preserving the security testing capabilities.
2. The existing Ansible playbooks are functioning correctly and follow best practices.
3. The deployment scripts for Chef Server and Automate need to be replaced with equivalent functionality using Ansible and potentially other tools.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The migration will maintain or improve the current security posture, particularly around SSL/TLS and SSH configurations.
6. No specific performance requirements were identified in the source repository.
7. The repository appears to be primarily for demonstration/example purposes rather than production use, based on the README content.