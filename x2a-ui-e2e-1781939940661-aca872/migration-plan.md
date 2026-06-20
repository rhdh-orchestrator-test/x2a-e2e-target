# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

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
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `index.html`: Sample HTML file used in the website deployment. Can be directly used in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider maintaining InSpec as a separate tool called from Ansible

- **Test Kitchen**: Replace with Molecule for testing Ansible roles and playbooks

### Security Considerations

- **SSL Configuration**: The poodle_fix.yml playbook addresses SSL security by enforcing TLSv1.2. This security practice should be maintained in the migrated Ansible playbooks.
  
- **SSH Security**: The ssh_profile.rb InSpec test checks for secure SSH configuration. This should be implemented as an Ansible task that both configures and verifies SSH security.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook; consider using Ansible Vault for storing pre-generated certificates or keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or other testing frameworks will require careful mapping of test logic.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions

- **Chef Automate/Server Deployment**: The bash scripts for Chef deployment will need to be completely rewritten as Ansible playbooks.
  - Mitigation: Research existing Ansible roles for similar deployments or create new roles based on the installation steps in the bash scripts

### Migration Order

1. **website_https.yml** (Priority 1, already Ansible): Review and optimize the existing Ansible playbook
2. **poodle_fix.yml** (Priority 1, already Ansible): Review and optimize the existing Ansible playbook
3. **InSpec Tests** (Priority 2): Convert InSpec tests to Ansible assertions or Molecule tests
4. **Chef Deployment Scripts** (Priority 3): Convert bash scripts to Ansible playbooks

### Assumptions

1. The primary goal is to consolidate all automation to Ansible, including testing that was previously done with InSpec.
2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are functional and can be used as-is or with minor modifications.
3. The target environment will continue to be Ubuntu 20.04 or compatible systems.
4. The deployment scripts for Chef Automate and Chef Infra Server will be replaced with equivalent Ansible playbooks that set up similar infrastructure or alternative solutions.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be properly secured in the migrated solution.
6. Test Kitchen will be replaced with Molecule or another Ansible-native testing framework.
7. The InSpec tests will need to be converted to equivalent Ansible tests or assertions.