# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on compliance automation and Chef Automate/Chef Infra Server deployment. The migration scope is relatively small, with two main components: (1) Chef InSpec tests used alongside Ansible playbooks for compliance automation, and (2) bash scripts for Chef Automate and Chef Infra Server deployment. The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef InSpec tests and bash scripts for Chef infrastructure deployment that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance automation
    - Path: chef-and-ansible/
    - Technology: Chef InSpec + Ansible
    - Key Features: HTTPS website deployment, SSL/TLS compliance testing, SSH security compliance

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts for Chef infrastructure deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration will require converting to Ansible Molecule or another Ansible testing framework.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Already in Ansible format, can be reused.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Already in Ansible format, can be reused.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment. Will need to be converted to Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Will need to be converted to Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Will need to be replaced with Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Will need to be replaced with Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Ansible Molecule for comprehensive testing
  - Option 4: Consider migrating to OpenSCAP with Ansible integration

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with Ansible alternatives:
  - Option 1: AWX/Ansible Tower for web UI, role-based access control, and job scheduling
  - Option 2: Ansible Semaphore for lightweight UI
  - Option 3: GitLab CI/CD with Ansible for pipeline-based automation

### Security Considerations

- **SSL/TLS Configuration**: The current implementation enforces TLSv1.2 and disables SSLv3 to prevent POODLE attacks. Migration should maintain or enhance this security posture.
  - Migration approach: Preserve the same SSL/TLS hardening in Ansible roles

- **SSH Security**: The repository includes SSH hardening profiles that disable root login.
  - Migration approach: Create an Ansible role for SSH hardening with the same controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed certificates generated in the Ansible playbook
  - Migration approach: Replace with Ansible Vault for credential storage and integrate with certificate management solutions

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks may require rethinking the testing approach.
  - Mitigation: Consider using Ansible's assert module for simple tests and Molecule for more complex scenarios.

- **Chef Automate Replacement**: Finding an equivalent to Chef Automate's compliance reporting in the Ansible ecosystem.
  - Mitigation: Evaluate AWX/Tower with compliance reporting plugins or integrate with external compliance tools.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - website_https.yml
   - poodle_fix.yml

2. **InSpec Tests** (Moderate complexity)
   - website_https_verify.rb
   - ssh_profile.rb

3. **Chef Deployment Scripts** (High complexity, dependencies)
   - deploy-chef-server.sh
   - deploy-automate.sh

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec integration with Ansible rather than being a production deployment.
2. The hardcoded credentials in the setup scripts are for demonstration purposes and not used in production.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs.
4. The migration will maintain the same level of security compliance checking currently provided by InSpec.
5. There are no external dependencies or integrations beyond what is visible in the repository.
6. The Chef Automate and Chef Infra Server deployment scripts are standalone and not part of a larger automation framework.