# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec profiles to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible components (which are already in Ansible format) and moderate complexity for converting the InSpec tests to Ansible-compatible testing frameworks.

## Module Migration Plan

This repository contains Chef InSpec profiles and Ansible playbooks that need individual migration planning:

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
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec profile that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing web server deployment. Can be directly used in Ansible without modification.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in assert module for basic testing
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Consider integrating with other testing frameworks like Testinfra or ServerSpec

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained during migration.
  - Migration approach: Preserve the same SSL protocol settings (TLSv1.2) and certificate generation process.

- **SSH Security**: The InSpec profile checks for SSH root login configuration.
  - Migration approach: Create equivalent Ansible tasks to verify and enforce SSH security settings.

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - Count of credentials detected: 3 (username, password, organization name in deployment scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation strategy: Map InSpec resources to equivalent Ansible modules or Molecule verifiers. For example, the port and http resources in InSpec can be tested using Ansible's wait_for and uri modules.

- **Chef Automate Deployment**: Replacing Chef Automate deployment with equivalent Ansible automation.
  - Mitigation strategy: If Chef Automate is still needed, create Ansible roles to deploy it. If not, identify alternative compliance and infrastructure management tools compatible with Ansible.

### Migration Order

1. Ansible playbooks (website_https.yml, poodle_fix.yml) - low risk, already in Ansible format
2. InSpec tests (website_https_verify.rb, ssh_profile.rb) - moderate complexity, requires conversion to Ansible testing framework
3. Chef deployment scripts (deploy-automate.sh, deploy-chef-server.sh) - high complexity, requires strategic decisions about replacing Chef infrastructure

### Assumptions

1. The primary goal is to consolidate on Ansible and remove Chef dependencies, including InSpec.
2. The current setup uses Chef InSpec primarily for testing, not for active configuration management.
3. There's no mention of whether Chef Automate and Chef Infra Server are required in the future state or if they should be replaced with Ansible-compatible alternatives.
4. The repository appears to be primarily for demonstration/educational purposes rather than production use, based on the README description.
5. The hardcoded credentials in the deployment scripts are example values and not actual production credentials.
6. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
7. There are no complex data structures or custom resources that would make migration particularly difficult.