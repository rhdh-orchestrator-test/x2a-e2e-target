# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. There are also Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible components (which are already in Ansible format) and moderate complexity for converting the InSpec tests to Ansible-native testing solutions.

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
    - Key Features: Disables SSLv3 and enables only TLSv1.2 in Apache configuration

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
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing. Migration consideration: Can be directly used in Ansible content.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider maintaining InSpec as a separate testing tool if deeply integrated

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Consider migration to:
  - Ansible Tower/AWX for orchestration and management
  - Ansible Content Collections for content distribution
  - GitLab/GitHub for version control and CI/CD

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Ensure these security configurations are preserved in the migrated Ansible roles.
  - Migration approach: Create dedicated Ansible role for Apache SSL configuration with the same security parameters.

- **SSH Security**: The InSpec tests verify SSH security configurations. Ensure these checks are maintained.
  - Migration approach: Create Ansible tasks that both configure and verify SSH security settings.

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook and should be handled securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions.
  - Mitigation strategy: Create a mapping document for InSpec resources to Ansible modules/assertions, use Molecule for integration testing.

- **Chef Server Deployment**: The Chef server deployment scripts need to be replaced with equivalent Ansible functionality.
  - Mitigation strategy: Create Ansible roles for configuration management server deployment (AWX/Tower).

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, just need refactoring to roles.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible testing framework.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, requires architectural decisions about replacement infrastructure.

### Assumptions

1. The primary goal is to move all functionality to Ansible, including testing that is currently done with InSpec.
2. The current setup uses Test Kitchen primarily for testing Ansible playbooks with InSpec, not for testing Chef cookbooks.
3. The deployment scripts for Chef Automate and Chef Infra Server are used for setting up the infrastructure, not for the actual application deployment.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production.
5. The target environment will continue to be Ubuntu 20.04 or compatible systems.
6. The SSL and security configurations are important to maintain in the migrated solution.
7. There may be additional Chef InSpec profiles or tests not explicitly included in this repository that might be referenced.