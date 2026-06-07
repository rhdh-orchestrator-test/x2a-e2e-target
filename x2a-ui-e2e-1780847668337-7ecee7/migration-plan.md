# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with most components already in Ansible format. The estimated timeline for complete migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login security check

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts using Chef CLI tools
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing web server functionality. No migration needed.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible's built-in assert module for basic tests
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Integrate with other compliance tools like OSCAP or Ansible Compliance

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve this security practice.
  - Migration approach: Use Ansible's `openssl_*` modules (already in use) with current best practices
  
- **SSH Hardening**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Implement equivalent checks using Ansible's assert module or Molecule verifiers

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates are generated during playbook execution
  - Count of credentials detected: 2 (username/password in deployment scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks may require additional tooling or custom modules.
  - Mitigation: Evaluate Molecule, Ansible assert module, or consider maintaining InSpec as a separate testing tool if necessary

- **Chef Server Deployment**: The Chef server deployment scripts need to be replaced with equivalent Ansible roles.
  - Mitigation: Create Ansible roles that can deploy alternative configuration management or compliance tools as needed

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
   - Only needs review and potential updates to follow current Ansible best practices
   
2. **poodle_fix.yml** (low risk, already in Ansible format)
   - Only needs review and potential updates to follow current Ansible best practices
   
3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible-native testing solutions
   
4. **Chef Deployment Scripts** (high complexity)
   - Replace with Ansible roles for deploying alternative tools if needed

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than to provide production-ready infrastructure code.
2. The Chef InSpec tests are used for compliance verification while Ansible handles the actual configuration.
3. The deployment scripts for Chef Automate and Chef Infra Server may not be needed after migration if an alternative compliance solution is chosen.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. There are no external dependencies or integrations beyond what's visible in the repository.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
7. The self-signed certificates are acceptable for the intended use case and don't need to be replaced with CA-signed certificates.