# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for configuring a web server with HTTPS
2. Chef InSpec tests for verifying compliance

Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be migrated to Ansible.

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a single developer to complete the migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **inspec-website-tests**:
    - Description: Chef InSpec tests that verify HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **inspec-ssh-profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Sample HTML file for testing web server. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Keep InSpec as a standalone tool but invoke it from Ansible
  - Option 4: Migrate to Ansible Molecule for testing

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Ensure the migration maintains or improves the security posture:
  - Maintain TLSv1.2 requirement
  - Consider upgrading to TLSv1.3 if supported
  - Ensure proper certificate handling

- **SSH Security**: The InSpec profile checks for SSH root login configuration. Ensure this security check is maintained in the Ansible migration.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be handled securely

### Technical Challenges

- **InSpec Test Migration**: Converting InSpec tests to Ansible assertions or another testing framework will require careful mapping of test functionality.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions.

- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be completely rewritten as Ansible playbooks.
  - Mitigation: Research Ansible roles for deploying alternative compliance and automation platforms.

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Add documentation and improve variable naming

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Consider merging with the website-https playbook

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible assertions or Molecule tests
   - Ensure all compliance checks are maintained

4. **Chef deployment scripts** (high complexity)
   - Rewrite as Ansible playbooks
   - Consider alternative compliance platforms if Chef Automate is not required

### Assumptions

1. The primary goal is to consolidate on Ansible and remove Chef dependencies where possible.
2. InSpec tests may need to be replaced with equivalent Ansible testing mechanisms.
3. The deployment scripts for Chef Automate and Chef Infra Server may need to be replaced with deployment scripts for alternative compliance platforms.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The security requirements (TLS configuration, SSH security) must be maintained or improved.
6. The repository appears to be a demonstration/example repository rather than production code, which may simplify migration decisions.