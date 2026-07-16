# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate to a pure Ansible solution. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

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
    - Description: Chef InSpec control that ensures SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing. Can be directly used in Ansible.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible alternatives:
  - For compliance testing: Use Ansible's built-in assert module or migrate to ansible-lint
  - For infrastructure validation: Use Ansible's built-in modules like stat, command, uri
  - Consider integrating with tools like Molecule for testing

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Consider migrating to:
  - AWX/Ansible Tower for orchestration
  - Ansible Collections for content organization
  - Git repositories for code storage and version control

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Ensure proper SSL/TLS settings are maintained during migration.
  - Migration approach: Use Ansible's apache2_module and copy modules to configure SSL properly

- **SSH Security**: The InSpec tests verify SSH security configurations. Ensure these checks are maintained.
  - Migration approach: Convert InSpec tests to Ansible assert tasks or use ansible-lint rules

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates are generated in the playbook and should be handled securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or other testing frameworks.
  - Mitigation strategy: Create equivalent Ansible tasks using assert module and uri module to verify the same conditions

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting capabilities.
  - Mitigation strategy: Consider integrating with AWX/Tower for reporting or use third-party compliance tools that integrate with Ansible

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format
2. InSpec Tests (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible assertions or Molecule tests
3. Chef Deployment Scripts (deploy-automate.sh, deploy-chef-server.sh) - Convert to Ansible roles for infrastructure setup

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are used for validation only and not for remediation
3. There are no external dependencies or integrations beyond what's visible in the repository
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. The migration will maintain the same functionality but consolidate everything to Ansible
6. No complex data migration is required as this appears to be primarily configuration code
7. The hardcoded credentials in the deployment scripts are for demonstration purposes only