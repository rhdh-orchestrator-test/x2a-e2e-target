# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together for compliance automation. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for continuous compliance validation. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with most content already in Ansible format. The estimated timeline for complete migration is 1-2 weeks, with low complexity for the Ansible playbooks (already in place) and moderate complexity for replacing the InSpec tests and Chef server deployment scripts.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening, service restart handlers

- **inspec_compliance_tests**:
    - Description: Chef InSpec tests for validating HTTPS configuration and SSH security settings
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS validation, SSL protocol verification, SSH root login security check

- **chef_automate_deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef_server_deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing the web server. No migration needed.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native solutions:
  - For compliance testing: Use Ansible Lint for static analysis
  - For runtime validation: Use the Ansible `assert` module or migrate to Molecule for testing
  - Alternative: Consider integrating with OpenSCAP or DISA STIG Ansible roles

- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and job scheduling
  - Ansible Galaxy for role management
  - Git repositories for version control

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. Migration should maintain or enhance this security posture.
  - Migration approach: Preserve the same SSL hardening in Ansible roles, consider updating to include TLS 1.3

- **SSH Hardening**: InSpec tests validate SSH root login is disabled.
  - Migration approach: Create Ansible roles that apply the same SSH hardening and include validation tasks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed certificates generated in the playbook
  - Migration approach: Replace with Ansible Vault for secrets management

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible validation tasks requires careful mapping of test assertions.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules, use assert module for validation

- **Chef Server Deployment**: Replacing Chef server deployment with Ansible Tower/AWX deployment requires different architecture.
  - Mitigation: Create Ansible playbooks that deploy AWX/Tower with similar user/organization structure

- **Compliance Validation**: Ensuring the same level of compliance validation without InSpec.
  - Mitigation: Consider using OpenSCAP with Ansible or implementing custom validation tasks

### Migration Order

1. **website_https playbook** (low risk, already in Ansible)
   - No migration needed, already in Ansible format
   - Consider refactoring into reusable roles

2. **poodle_fix playbook** (low risk, already in Ansible)
   - No migration needed, already in Ansible format
   - Consider combining with website_https into a comprehensive web server role

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible assert tasks or Molecule tests
   - Create validation playbooks that perform the same checks

4. **Chef deployment scripts** (high complexity)
   - Create Ansible playbooks to deploy Ansible Tower/AWX
   - Implement user/organization management through Tower API or manual processes

### Assumptions

1. The primary goal is to move all functionality to Ansible, eliminating Chef components
2. The InSpec tests are critical for compliance and their functionality must be preserved
3. The deployment scripts are used for setting up infrastructure and need equivalent Ansible solutions
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. There are no external dependencies or integrations not visible in the repository
6. The hardcoded credentials in the deployment scripts are not used in production
7. The self-signed certificates are acceptable for the environment (not production)
8. The Apache version pinning (2.4.41-4ubuntu3.10) is intentional and should be maintained