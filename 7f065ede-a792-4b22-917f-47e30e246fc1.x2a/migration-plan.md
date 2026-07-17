# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef server deployment scripts that need to be converted to Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and clear separation of concerns.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing
    - Path: chef-and-ansible
    - Technology: Chef InSpec (tests) and Ansible (playbooks)
    - Key Features: HTTPS website deployment, SSL/TLS compliance testing, Test Kitchen integration

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef server deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible integration with InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Can be preserved as-is in the migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be preserved as-is in the migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Needs conversion to Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Needs conversion to Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs conversion to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs conversion to Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but deployment scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic compliance testing
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing (recommended)
  - Option 4: Consider integrating with OpenSCAP or DISA STIG tools for compliance testing

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and control
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance scanning tools like OpenSCAP or Ansible Compliance as Code

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the secure TLS 1.2 configuration and disabled SSL3 as verified in the InSpec tests
- **SSH Security**: The SSH root login restrictions must be maintained in the migrated solution
- **Self-signed Certificates**: The certificate generation process should be preserved in the Ansible playbooks
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets identified in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require careful mapping of test assertions and compliance checks
  - Mitigation: Create a mapping document for InSpec resources to Ansible assertions
  
- **Chef Server Deployment**: Replacing Chef server deployment with equivalent Ansible functionality
  - Mitigation: Use Ansible Tower/AWX as the central management platform and implement equivalent user/organization management

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - `website_https.yml`
   - `poodle_fix.yml`

2. **InSpec Tests** (Moderate complexity)
   - `website_https_verify.rb`
   - `ssh_profile.rb`

3. **Chef Server Deployment Scripts** (High complexity)
   - `deploy-chef-server.sh`
   - `deploy-automate.sh`

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment
2. The Chef InSpec tests are used for compliance verification of Ansible-deployed infrastructure
3. The deployment scripts are examples and not used in production environments
4. No external dependencies or cookbooks are being used beyond what's visible in the repository
5. The target environment is Ubuntu 20.04 running on Vagrant VMs
6. There are no complex data structures or state management requirements
7. The migration will preserve all existing functionality while moving to pure Ansible
8. No custom Chef resources or complex Chef-specific functionality is being used