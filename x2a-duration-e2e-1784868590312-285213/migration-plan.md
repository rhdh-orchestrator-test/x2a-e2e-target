# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for continuous compliance. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the content is already in Ansible format. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Adapting the Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

Estimated timeline: 1-2 weeks for a complete migration, with minimal complexity due to the limited scope of Chef-specific components.

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
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance tagging (STIG, CCI)

- **deploy-automate**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **deploy-chef-server**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used as a test page. Migration consideration: Can be used as-is or templated in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks
  - Option 4: Consider OpenSCAP integration for STIG compliance checks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and control
  - Ansible Collections for configuration management
  - GitLab CI/GitHub Actions for pipeline automation

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS settings are maintained during migration.
  - Migration approach: Use Ansible's apache2_module and apache2_conf modules with identical SSL settings

- **SSH Hardening**: The InSpec tests verify SSH security configurations.
  - Migration approach: Create equivalent Ansible tasks to enforce the same SSH security controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible assertions or other testing frameworks.
  - Mitigation: Create a mapping of InSpec resources to Ansible modules and assertions

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated.
  - Mitigation: Integrate with Ansible Tower/AWX for reporting or use additional tools like OpenSCAP

- **Chef Server Deployment**: The Chef server deployment scripts need to be converted to Ansible playbooks.
  - Mitigation: Create equivalent Ansible roles for server deployment or consider if Chef server is still needed after migration

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (already in Ansible format, low risk)
2. **InSpec Tests** (moderate complexity, convert to Ansible-native testing)
3. **Chef Deployment Scripts** (high complexity, requires designing Ansible alternatives)

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment.
2. The Chef Automate and Chef Infra Server deployment scripts are examples and not actively used in production.
3. The security compliance requirements (STIG, CCI) mentioned in the InSpec tests are still relevant and need to be maintained.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The self-signed certificates used in the examples are for demonstration purposes and would be replaced with proper certificates in production.
6. The hardcoded credentials in the deployment scripts are examples and not actual production credentials.