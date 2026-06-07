# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together for compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, as most of the configuration is already in Ansible format, with Chef InSpec being used for compliance testing. The migration will primarily involve replacing Chef InSpec tests with Ansible-native testing solutions.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used for testing web server functionality

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace with Ansible Molecule for testing
  - Convert InSpec tests to Ansible assert tasks or Molecule verify steps
  - Consider using ansible-lint for static analysis

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Infra Server**: If compliance reporting is needed, consider:
  - Ansible AWX/Tower for orchestration
  - Compliance solutions like OpenSCAP or Ansible's built-in compliance capabilities

### Security Considerations

- **SSL Configuration**: The migration must maintain the security improvements in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enforced
  - Consider updating to also include TLSv1.3 support

- **SSH Security**: The SSH compliance checks in ssh_profile.rb must be preserved
  - Convert the InSpec control to equivalent Ansible assertions
  - Maintain compliance with security standards (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module and custom modules where needed
  - Consider using community.general collection for enhanced testing capabilities

- **Compliance Reporting**: If compliance reporting is a requirement, finding an Ansible-native solution
  - Mitigation: Evaluate OpenSCAP integration or Ansible AWX/Tower compliance features

- **Test Kitchen Replacement**: Ensuring Molecule provides equivalent functionality
  - Mitigation: Create detailed Molecule scenarios that match the current Test Kitchen setup

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format
   - Review and update to current Ansible best practices
   - Ensure idempotency and proper error handling

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Medium complexity
   - Convert to Ansible Molecule tests
   - Ensure equivalent coverage and assertions

3. **Chef Automate/Server Deployment Scripts** - Higher complexity
   - Convert bash scripts to Ansible roles for server provisioning
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is for demonstration/example purposes rather than production use, as indicated by the README.md.

2. The Chef InSpec tests are used primarily for compliance verification and can be replaced with equivalent Ansible testing mechanisms.

3. The deployment scripts for Chef Automate and Chef Infra Server may not be needed if the goal is to fully migrate to Ansible, unless there's a requirement to maintain a Chef infrastructure alongside Ansible.

4. The Test Kitchen configuration is used for development and testing purposes and can be replaced with Ansible Molecule.

5. There are no external dependencies or integrations beyond what's visible in the repository.

6. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with proper secret management in a production environment.

7. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.