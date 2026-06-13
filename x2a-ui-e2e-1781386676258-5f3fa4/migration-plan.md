# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
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
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used as a test page. Migration consideration: Keep as-is or include in Ansible templates.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible alternatives:
  - Option 1: Use Ansible's built-in assert module for basic compliance checks
  - Option 2: Integrate with ansible-lint for static code analysis
  - Option 3: Use Ansible's community.general.inspec module to continue using InSpec tests
  - Option 4: Migrate to Ansible Molecule for testing

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL configuration is maintained during migration.
  - Migration approach: Use Ansible's openssl_* modules as already implemented in the existing playbooks.

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Convert InSpec tests to Ansible assert tasks or continue using InSpec via the community.general.inspec module.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible's testing capabilities.
  - Mitigation strategy: Use Ansible's assert module for basic tests, or maintain InSpec tests and run them via Ansible's community.general.inspec module.

- **Chef Automate Deployment**: Replacing Chef Automate deployment scripts with Ansible equivalents.
  - Mitigation strategy: Create Ansible roles for deploying alternative compliance and infrastructure management tools, or create Ansible playbooks that can deploy Chef Automate if it needs to be maintained.

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already in Ansible format)
2. **InSpec tests** (moderate complexity, requires conversion to Ansible testing format)
3. **Chef deployment scripts** (high complexity, requires replacement with Ansible alternatives)

### Assumptions

1. The primary goal is to consolidate on Ansible and remove Chef dependencies where possible.
2. The InSpec tests are valuable and should be preserved in some form.
3. The Chef Automate and Chef Infra Server deployment may be replaced with alternative tools or maintained but deployed via Ansible.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The security requirements specified in the InSpec tests must be maintained.
6. The repository is primarily used for demonstration and educational purposes rather than production deployments.
7. No external dependencies or complex integrations exist beyond what is visible in the repository.