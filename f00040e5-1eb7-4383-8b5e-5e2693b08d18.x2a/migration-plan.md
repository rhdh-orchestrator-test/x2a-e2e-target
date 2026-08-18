# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration will involve consolidating these technologies into a pure Ansible solution, leveraging Ansible's native testing capabilities or integrating with other testing frameworks.

The repository is relatively small and focused, containing:
- 2 Ansible playbooks for configuring web servers with HTTPS
- 2 Chef InSpec test files for verifying compliance
- 2 Shell scripts for deploying Chef Automate and Chef Infra Server

Estimated migration complexity: **Low to Medium**
Estimated timeline: **1-2 weeks**

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS is properly configured on port 443
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, security compliance check

- **chef-automate-deployment**:
    - Description: Shell script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Shell script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Static HTML content for the web server. Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks
  - Option 4: Consider migrating to OpenSCAP or DISA STIG tools that integrate with Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible Tower/AWX for orchestration and testing

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks for deploying alternative compliance platforms
  - Consider migrating to Ansible Tower/AWX for centralized management

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Migration must maintain:
  - Self-signed certificate generation
  - Proper SSL protocol configuration (TLSv1.2 only)
  - Virtual host SSL configuration

- **SSH Hardening**: The InSpec tests verify SSH security. Migration must:
  - Implement equivalent checks for SSH root login
  - Maintain compliance with security standards referenced (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or other testing frameworks will require:
  - Understanding the compliance requirements being tested
  - Implementing equivalent checks using Ansible modules
  - Ensuring the same level of reporting and documentation

- **Deployment Script Migration**: The Chef deployment scripts need to be converted to:
  - Ansible playbooks that can deploy alternative compliance platforms
  - Or documentation on how to use Ansible Tower/AWX instead

### Migration Order

1. **website_https.yml** (Priority 1): Already an Ansible playbook, requires minimal changes
2. **poodle_fix.yml** (Priority 1): Already an Ansible playbook, requires minimal changes
3. **InSpec Tests** (Priority 2): Convert to Ansible-native testing solutions
4. **Deployment Scripts** (Priority 3): Replace with Ansible playbooks or documentation

### Assumptions

1. The primary goal is to consolidate on Ansible and remove Chef InSpec dependencies
2. The compliance requirements in the InSpec tests must be maintained in the Ansible solution
3. The deployment scripts for Chef Automate/Infra Server are not critical to the application functionality but are used for setting up the management platform
4. Test Kitchen is only used for development/testing and not in production
5. No external Chef cookbooks or recipes are being used beyond what's visible in the repository
6. The target environment will continue to be Ubuntu 20.04 or compatible systems
7. The self-signed certificates are acceptable for the environment (not production)
8. No external dependencies or integrations beyond what's visible in the code