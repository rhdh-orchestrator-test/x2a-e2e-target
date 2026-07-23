# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that are used together to deploy and validate secure web server configurations. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The repository also includes scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks (which can be kept largely as-is) and moderate complexity for converting the InSpec tests to Ansible-native testing solutions.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
I have verified that there are no Puppet modules (no manifests/init.pp files), no Chef cookbooks (no recipes/default.rb files), and no PowerShell modules (no .psd1 files) in this repository. The repository primarily contains Ansible playbooks and Chef InSpec tests.

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
    - Description: Chef InSpec test that validates HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol validation

- **ssh_profile**:
    - Description: Chef InSpec profile that validates SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Static HTML content for the web server. Migration consideration: Keep as-is, no changes needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security hardening should be preserved in the migrated solution.
  - Migration approach: Keep the same SSL configuration parameters in the Ansible tasks

- **SSH Security**: The InSpec tests validate SSH security configurations (disabling root login).
  - Migration approach: Convert InSpec tests to Ansible assert tasks or Molecule tests

- **Self-signed Certificates**: The playbook generates self-signed certificates for HTTPS.
  - Migration approach: Keep the same certificate generation tasks using Ansible's openssl modules

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions will require understanding the equivalent assertions.
  - Mitigation: Use Ansible's assert module for basic validation and consider Molecule for more comprehensive testing.

- **Chef Automate/Server Deployment**: The bash scripts for deploying Chef Automate and Chef Infra Server will need to be converted to Ansible playbooks.
  - Mitigation: Create equivalent Ansible roles for Chef server deployment, or consider if these components are still needed after migration.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, can be kept largely as-is with minor adjustments to follow best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible assert tasks or Molecule tests
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible roles or evaluate if still needed

### Assumptions

1. The primary goal is to migrate away from Chef InSpec while keeping or enhancing the Ansible components
2. The deployment scripts for Chef Automate and Chef Infra Server may not be needed after migration if the purpose is to move entirely to Ansible
3. The security testing and validation currently done with InSpec is still required in the migrated solution
4. The target environment (Ubuntu 20.04) will remain the same after migration
5. Test Kitchen is currently used for development and testing, and an equivalent workflow will be needed in the migrated solution
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migrated solution