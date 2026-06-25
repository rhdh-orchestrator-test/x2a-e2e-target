# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for configuring a web server with HTTPS
2. Chef InSpec tests for verifying compliance

Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be migrated to Ansible.

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and the fact that part of the infrastructure is already using Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec-compliance-tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login testing

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Sample HTML file used for testing the web server. Can be directly used in Ansible content.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with ansible-lint for static analysis
  - Option 3: Use Ansible collections like ansible.posix and community.general for system checks
  - Option 4: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: The InSpec profile checks for SSH root login being disabled
  - Ensure this security check is maintained in the Ansible migration

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed certificates generated in website_https.yml
  - Consider using Ansible Vault to secure these credentials

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible assertions or checks
  - Mitigation: Use Ansible's assert module with appropriate conditions or maintain InSpec as a separate tool called from Ansible

- **Chef Automate Deployment**: Migrating the Chef Automate deployment scripts to Ansible
  - Mitigation: Create Ansible roles for Chef Automate and Chef Server deployment, or consider replacing with pure Ansible infrastructure

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Add documentation and improve variable naming

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Consider merging with website-https as a role

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible assertions or maintain as separate InSpec tests
   - Ensure all compliance checks are preserved

4. **Chef Automate deployment scripts** (high complexity)
   - Create Ansible playbooks to replace the bash scripts
   - Consider if Chef Automate is still needed or if it can be replaced with Ansible Tower/AWX

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.md.

2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are already working correctly and don't need significant changes.

3. The target environment is Ubuntu 20.04 as specified in kitchen.yml.

4. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a test environment and may not be needed in a pure Ansible workflow.

5. There's no complex data structure or state management that would require special handling during migration.

6. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with proper secret management in production.