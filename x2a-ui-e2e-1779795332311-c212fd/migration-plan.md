# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing rather than being a pure Chef cookbook repository. The migration scope is relatively small, as most of the infrastructure code is already in Ansible format, with Chef components primarily being used for testing and compliance validation.

**Timeline Estimate**: 1-2 weeks
**Complexity**: Low to Medium
**Primary Focus**: Converting InSpec tests to Ansible-native testing solutions

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

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
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef Server CLI
    - Key Features: Chef server setup, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing web server functionality. No migration needed.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be environment-agnostic with potential for on-premises or cloud deployment (based on setup-automate scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible's built-in `assert` module for basic testing
  - Option 2: Molecule for more comprehensive testing
  - Option 3: Use community.general.test_connection module for connectivity tests

- **Test Kitchen with Vagrant**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Consider migrating to:
  - Ansible Tower/AWX for orchestration and management
  - Ansible Content Collections for compliance profiles

### Security Considerations

- **SSL Configuration**: The repository includes SSL hardening (disabling SSLv3, enabling TLSv1.2). Ensure these security configurations are maintained in the Ansible migration.
  
- **SSH Security**: The InSpec test checks for SSH root login being disabled. Ensure this security check is maintained in the Ansible migration.

- **Self-signed Certificates**: The playbook generates self-signed certificates. Consider implementing a more robust certificate management solution in the migration.

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - SSL certificate and key files generated and stored in /etc/apache2/certs
  - Recommend implementing Ansible Vault for credential storage in the migration

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing solutions will require understanding the specific assertions and checks being performed.
  - Mitigation: Map InSpec resources to equivalent Ansible modules and assertions.

- **Compliance Validation**: Maintaining the compliance validation capabilities currently provided by InSpec.
  - Mitigation: Evaluate Ansible's compliance capabilities or integrate with other compliance tools.

- **Chef Server Deployment**: The bash scripts for Chef server deployment will need to be converted to Ansible playbooks.
  - Mitigation: Create equivalent Ansible roles for Chef server deployment or replace with Ansible Tower/AWX.

### Migration Order

1. **website_https_verify.rb** (Medium complexity, high value): Convert InSpec tests to Ansible assertions or Molecule tests
2. **ssh_profile.rb** (Medium complexity): Convert InSpec compliance control to Ansible security role
3. **setup-automate scripts** (High complexity): Convert bash scripts to Ansible roles for deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance testing, not to provide production-ready infrastructure code.

2. The InSpec tests are the main components that need migration, as the infrastructure code is already in Ansible format.

3. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.

4. The security configurations (SSL hardening, SSH security) are important aspects that must be maintained in the migration.

5. The Chef Automate and Chef Infra Server deployment scripts are examples and may not be actively used in production.

6. There are no external dependencies or complex integrations beyond what is visible in the repository.

7. The migration will focus on maintaining the same functionality while converting to pure Ansible solutions.