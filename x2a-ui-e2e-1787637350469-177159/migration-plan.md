# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The complexity is low to moderate, as the existing Ansible playbooks can be largely reused, while the InSpec tests need to be converted to Ansible-native solutions. Estimated timeline: 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

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
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

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

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used in the website deployment. Migration consideration: Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider migrating to OpenSCAP or DISA STIG Ansible roles

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained during migration.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented in the existing playbooks.

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Create Ansible tasks using the `lineinfile` or `template` modules to configure SSH properly, and use Ansible's `assert` module to verify the configuration.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates are generated in the playbook; consider using Ansible Vault for storing private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or another testing framework.
  - Mitigation strategy: Use Ansible's `uri` module to replace HTTP checks and `command`/`shell` modules with `assert` for other verifications.

- **Chef Automate/Server Deployment**: The bash scripts deploy Chef Automate and Chef Infra Server.
  - Mitigation strategy: Create Ansible roles to replace these scripts, potentially using the `command` module to run the Chef Automate CLI commands if needed.

### Migration Order

1. **website_https.yml** (Priority 1, low risk): Already an Ansible playbook, minimal changes needed
2. **poodle_fix.yml** (Priority 1, low risk): Already an Ansible playbook, minimal changes needed
3. **InSpec Tests** (Priority 2, moderate complexity): Convert to Ansible assertions or Molecule tests
4. **Chef Deployment Scripts** (Priority 3, high complexity): Convert to Ansible roles for Chef infrastructure deployment

### Assumptions

1. The primary goal is to migrate all functionality to pure Ansible without relying on Chef components.
2. The InSpec tests are used for compliance verification and need to be replaced with equivalent Ansible functionality.
3. The deployment scripts for Chef Automate and Chef Infra Server may not need migration if the goal is to move away from Chef entirely.
4. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and can be incorporated into the new Ansible structure with minimal changes.
5. Test Kitchen is currently used for testing the Ansible playbooks, and this will be replaced with an Ansible-native testing solution.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migrated solution.